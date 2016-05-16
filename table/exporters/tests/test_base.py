import io
import unittest

from table.exporters.base import Exporter
from table.table import ListTable


class RandomExporter(Exporter):
    def __init__(self, n):
        self.n = n

    def dump(self, table, fo, encoding_hint="utf-8"):
        for i in map(str, range(self.n)):
            fo.write(i.encode(encoding_hint))


class ErrorExporter(Exporter):
    def dump(self, table, fo, encoding_hint="utf-8"):
        fo.write(b"OK")
        raise ValueError("Woops.")


class TestBaseExporter(unittest.TestCase):
    def test_randomised(self):
        """Methods such as dump_iter use threads. We test their implementation by running it
        through thousands of randomised values in order to detect threading issues."""
        table = ListTable(rows=[], columns=[])
        re = RandomExporter(n=1000)

        # Test dump()
        buffer = io.BytesIO()
        re.dump(table, buffer)
        expected = "".join(map(str, range(1000))).encode()
        self.assertEqual(expected, buffer.getvalue())

        # Test dump_iter()
        for i, enc in enumerate(re.dump_iter(table)):
            self.assertEqual(str(i).encode(), enc)
        self.assertEqual(1000, sum(1 for _ in re.dump_iter(table)))

    def test_error_handling_dump_iter(self):
        """Are error messages correctly surfaced?"""
        table = ListTable(rows=[], columns=[])
        seq = ErrorExporter().dump_iter(table)
        self.assertRaises(ValueError, list, seq)
