import csv

from table.exporters.base import Exporter


class CSVExporter(Exporter):
    extension = "csv"
    content_type = "text/csv"

    def __init__(self, dialect="excel", **fmtparams):
        self.dialect = dialect
        self.fmtparams = fmtparams

    def dump(self, table, fo, encoding_hint="utf-8"):
        csvf = csv.writer(fo, dialect=self.dialect, **self.fmtparams)
        csvf.writerow([c.label for c in table.column])
        for row in table.rows:
            csvf.writerow([column.to_str(value) for column, value in zip(row, table.columns)])
