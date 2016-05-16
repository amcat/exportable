import itertools
import pyexcel

from amcatable.exporters.base import Exporter


class PyExcelExporter(Exporter):
    def dump(self, table, fo, filename_hint=None, encoding_hint="utf-8"):
        colnames = [col.verbose_name for col in table.columns]
        sheet1 = itertools.chain([colnames], table.rows)
        book = pyexcel.Book(sheets={"Sheet 1": sheet1})
        self.dump_book(book, fo, encoding_hint=encoding_hint)

    def dump_book(self, book: pyexcel.Book, fo, encoding_hint="utf-8"):
        book.save_to_memory(self.extension, fo)


class ODSExporter(PyExcelExporter):
    extension = "ods"
    content_type = "application/vnd.oasis.opendocument.spreadsheet"


class XLSExporter(PyExcelExporter):
    extension = "xls"
    content_type = "application/vnd.ms-excel"


class XLSXExporter(PyExcelExporter):
    extension = "xlsx"
    content_type = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"


#class CSVExporter(PyExcelExporter):
#    extension = "csv"
#    content_type = "text/csv"
