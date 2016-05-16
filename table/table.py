from typing import Iterable, Any, Sequence, Union
from collections import OrderedDict
from table.columns import Column


class LazyTableError(Exception):
    pass


class Table:
    def __init__(self, rows: Union[Iterable[Any], Sequence[Any]], columns: Sequence[Column], lazy=True, size_hint=None):
        """

        @param rows: list of rows
        @param columns: list of columns
        @param lazy: if True, no random access is allowed
        @param size_hint: (approximate) length of rows. Is used by exporters to determine progress.
        """
        # If no size_hint is given, try to guess the size by querying rows.
        if size_hint is None:
            try:
                self.size_hint = len(rows)
            except TypeError:
                self.size_hint = None
        else:
            self.size_hint = size_hint

        self.lazy = lazy
        self._rows = iter(rows) if lazy else rows
        self._columns = list(columns)

        self._column_indices_rev = OrderedDict((c, i) for i, c in enumerate(self._columns))
        self._column_view_indices = OrderedDict((i, c) for i, c in enumerate(self._columns) if c)
        self._column_view_indices_rev = OrderedDict((c, i) for i, c in enumerate(self._columns) if c)

    @property
    def columns(self) -> Iterable[Column]:
        return filter(None, self._columns)

    @property
    def rows(self):
        raise NotImplementedError("Subclasses should implement rows().")

    def get_row(self, index):
        if self.lazy:
            raise LazyTableError("You cannot access rows by index on a lazy table")
        return self._rows[index]

    def get_column(self, column: Column):
        if self.lazy:
            raise LazyTableError("You cannot access a single column on a lazy table")
        column_index = self._column_view_indices_rev[column]
        return (row[column_index] for row in self.rows)

    def get_value(self, row, column: Column):
        return self.get_row(row)[self._column_view_indices[column]]

    def dump(self, fo, exporter, encoding_hint=None):
        return exporter.dump(self, fo, encoding_hint=encoding_hint)

    def dumps(self, exporter, encoding_hint=None):
        return exporter.dumps(self, encoding_hint=encoding_hint)


class ListTable(Table):
    def __init__(self, rows: Iterable[Sequence[Any]], columns, lazy=True, size_hint=None):
        """
        @param rows: list of rows
        @param columns: if a column is None, skip a field in each row
        @param lazy: if True, no random access is allowed
        @param size_hint: (approximate) length of rows. Is used by exporters to determine progress.
        """
        super().__init__(rows, columns, lazy=lazy, size_hint=size_hint)

    @property
    def rows(self):
        for row in self._rows:
            yield [row[ci] for ci in self._column_view_indices]


class DictTable(Table):
    def __init__(self, rows: Iterable[dict], columns, allow_missing=False, lazy=True, size_hint=None):
        """
        @param rows: list of rows
        @param columns: list of columns. The label of a column is used to access dictionary.
        @param lazy: if True, no random access is allowed
        @param size_hint: (approximate) length of rows. Is used by exporters to determine progress.
        """
        self.allow_missing = allow_missing
        super().__init__(rows, columns, lazy=lazy, size_hint=size_hint)


    @property
    def rows(self):
        if self.allow_missing:
            # Do not throw an error when some column is not found in dictionary
            for row in self._rows:
                yield [row.get(c.label) for c in self.columns]
        else:
            # DO yield errors upon missing data
            for row in self._rows:
                yield [row[c.label] for c in self.columns]


