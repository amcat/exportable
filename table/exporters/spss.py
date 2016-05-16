import subprocess
import itertools
import tempfile
from zipfile import ZipFile

import dateutil.parser
import re
import datetime
import collections
import os.path
import logging
import shutil

from table.columns import Column
from table.exporters.base import Exporter
from table.table import Table

log = logging.getLogger(__name__)


# Do not let PSPP documentation get in the way of writing proper PSPP input :)
MAX_STRING_LENGTH = 32767 # PSPP Maximum per: http://bit.ly/1SVPNfU

PSPP_TYPES = {
    int: "F8.0",
    str: "A{}".format(MAX_STRING_LENGTH),
    float: "DOT9.2",
    datetime.datetime: "DATETIME20"
}

PSPP_SERIALIZERS = {
    type(None): lambda n: "",
    str: lambda s: s.replace('\n', ". ").replace("\r", "").replace("\t", " ")[:MAX_STRING_LENGTH],
    datetime.datetime: lambda d: d.strftime("%d-%b-%Y-%H:%M:%S").upper()
}

PSPP_COMMANDS = r"""
GET DATA
    /type=txt
    /file="{txt}"
    /encoding="utf-8"
    /arrangement=delimited
    /delimiters="\t"
    /qualifier=""
    /variables {variables}.
SAVE OUTFILE='{sav}'.
"""

PSPP_VERSION_RE = re.compile(b"pspp \(GNU PSPP\) (\d+)\.(\d+).(\d+)")
PSPPVersion = collections.namedtuple("PSPPVersion", ["major", "minor", "micro"])


def get_pspp_version() -> PSPPVersion:
    try:
        process = subprocess.Popen(["pspp", "--version"], stdout=subprocess.PIPE)
    except FileNotFoundError:
        raise FileNotFoundError("Could not execute pspp. Is it installed?")

    stdout, _ = process.communicate()
    for line in stdout.splitlines():
        match = PSPP_VERSION_RE.match(line)
        if match:
            return PSPPVersion(*map(int, match.groups()))

    raise PSPPError("Could not find version of installed pspp.")


def get_var_name(col: Column, seen: set):
    fn = str(col).replace(" ", "_")
    fn = fn.replace("-", "_")
    fn = re.sub('[^a-zA-Z_]+', '', fn)
    fn = re.sub('^_+', '', fn)
    fn = fn[:16]
    if fn in seen:
        for i in itertools.count():
            if "%s_%i" % (fn, i) not in seen:
                fn = "%s_%i" % (fn, i)
                break
    seen.add(fn)
    return fn


def serialize_spss_value(typ, value, default=lambda o: str(o)):
    return PSPP_SERIALIZERS.get(typ, default)(value)


def table2pspp(table: Table, saveas: str):
    # Deduce cleaned variable names and variable types
    seen = set()
    varnames = {col: get_var_name(col, seen) for col in table.columns}

    variables = []
    for col in table.columns:
        # HACK: Forcefully set column with name date  to datetime
        if col.label == "date":
            variables.append(("date", PSPP_TYPES[datetime.datetime]))
        else:
            variables.append((varnames[col], PSPP_TYPES[col.type]))
    variables = " ".join(map(str, itertools.chain.from_iterable(variables)))

    # Open relevant files (reopen so we're sure that we're writing utf-8)
    _, txt = tempfile.mkstemp(suffix=".txt")
    txt = open(txt, "w", encoding="utf-8")

    # Write table in tab separated format
    for row in table.rows:
        for i, col in enumerate(table.columns):
            if i: txt.write("\t")
            value = table.get_value(row, col)

            # HACK: forcefully convert column 'date' to datetime
            if value is not None:
                if col.label == "date":
                    txt.write(serialize_spss_value(datetime.datetime, dateutil.parser.parse(value)))
                else:
                    txt.write(serialize_spss_value(col.type, value))
        txt.write("\n")

    return txt.name, PSPP_COMMANDS.format(txt=txt.name, sav=saveas, variables=variables)


class PSPPError(Exception):
    pass


def table2sav(table: Table):
    _, sav = tempfile.mkstemp(suffix=".sav", prefix="table-")

    log.debug("Check if we've got the right version of PSPP installed")
    version = get_pspp_version()
    if version < PSPPVersion(0, 8, 5):
        raise PSPPVersion("Expected pspp>=8.5.0, but found {}".format(version))

    log.debug("Starting PSPP")
    pspp = subprocess.Popen(
        ["pspp", "-b"],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE
    )

    log.debug("Generating SPSS code..")
    txt, pspp_code = table2pspp(table, sav)

    log.debug("Encoding PSPP code as ASCII..")
    pspp_code = pspp_code.encode("ascii")

    log.debug("Sending code to pspp..")
    stdout, stderr = pspp.communicate(input=pspp_code)
    os.unlink(txt)

    stdout = stdout.decode("utf-8")
    stderr = stderr.decode("utf-8")

    log.debug("PSPP stderr: %s" % stderr)
    log.debug("PSPP stdout: %s" % stdout)

    stderr = stderr.replace('pspp: error creating "pspp.jnl": Permission denied', '')
    stdout = stdout.replace('pspp: ascii: opening output file "pspp.list": Permission denied', '')

    if stderr.strip():
        raise PSPPError(stderr)
    if "error:" in stdout.lower():
        raise PSPPError("PSPP Exited with error: \n\n%s" % stdout)
    if not os.path.exists(sav):
        raise PSPPError("PSPP Exited without errors, but file was not saved.\n\nOut=%r\n\nErr=%r" % (stdout, stderr))
    return sav


class SPSSExporter(Exporter):
    extension = "sav"
    content_type = "application/x-spss-sav"

    def dump(self, table, fo, filename_hint=None, encoding_hint="utf-8"):
        # Writing lazily not possible due to desgin of PSPP.
        # TODO: Implement named pipes to prevent storing intermediate results on disk
        sav = open(table2sav(table), "rb")

        # Unlinking before reading is save on Linux. Even if copying goes wrong, Linux will
        # cleanup the disk for us.
        os.unlink(sav.name)

        # Copy in chunks
        shutil.copyfileobj(sav, fo)


class ZippedSPSSExporter(Exporter):
    extension = "sav.zip"
    content_type = "application/zip"

    def dump(self, table, fo, filename_hint=None, encoding_hint="utf-8"):
        with ZipFile(fo, mode="wb") as zip:
            file = table2sav(table)
            try:
                zip.write(file, arcname=filename_hint)
            finally:
                os.unlink(file)
