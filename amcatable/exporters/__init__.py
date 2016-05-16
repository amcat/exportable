from amcatable.exporters.csv import CSVExporter
from amcatable.exporters.pyexcel import ODSExporter, XLSXExporter, XLSExporter
from amcatable.exporters.spss import SPSSExporter, ZippedSPSSExporter

DEFAULT_EXPORTERS = [
    ODSExporter,
    XLSXExporter,
    XLSExporter,
    CSVExporter,
    SPSSExporter,
    ZippedSPSSExporter
]


def get_exporter_by_extension(extension):
    for exporter in DEFAULT_EXPORTERS:
        if exporter.extension == extension:
            return exporter
    raise ValueError("No exporter with extension {} in DEFAULT_EXPORTERS.".format(extension))