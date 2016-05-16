import datetime
import dateutil.parser


class Column(object):
    type = None

    def __init__(self, label, verbose_name=None):
        self.label = label
        self.verbose_name = label if verbose_name is None else verbose_name

    def from_str(self, s):
        """Convert value from str. Might be used by importers which support all formats."""
        return self.type(s) if s else None

    def to_str(self, value):
        """Convert value into string representation. Might be used by exporters which file
        format does not support types or specific types."""
        return "" if value is None else str(value)


class TextColumn(Column):
    type = str

    def to_str(self, value):
        return value


class IntColumn(Column):
    type = int


class FloatColumn(Column):
    type = float


class DateColumn(Column):
    type = datetime.date

    def from_str(self, s) -> datetime.date:
        return dateutil.parser.parse(s).date() if s else None

    def to_str(self, date: datetime.date):
        return date.isoformat()


class DateTimeColumn(Column):
    type = datetime.datetime

    def from_str(self, s) -> datetime.datetime:
        return dateutil.parser.parse(s) if s else None

    def to_str(self, time: datetime.datetime):
        return time.isoformat()
