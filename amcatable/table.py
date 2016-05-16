import copy
import itertools

from typing import Iterable, Any, Sequence, Union
from amcatable.columns import Column


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
        self._rows = iter(rows) if lazy else list(rows)
        self._columns = [copy.copy(column) for column in columns]

        for i, column in enumerate(self._columns):
            if column.label is None:
                error = "Each column MUST have a label upon amcatable instantiation. {} ({}) has none."
                raise ValueError(error.format(column, i))

        # Set index on each column object. Notice that we skip None columns on purpose, but
        # still increase the counter by one. This is useful for ListTable (and doesn't
        # impact other implementations).
        self._column_counter = itertools.count()
        view_index = 0
        for column in self._columns:
            index = next(self._column_counter)
            if column is not None:
                column._index = index
                column._view_index = view_index
                view_index += 1

    def to_strict(self):
        """Convert this (lazy) amcatable into a non-lazy (strict) one."""
        if self.lazy:
            self._rows = list(self._rows)
            self.lazy = False

    @property
    def columns(self) -> Iterable[Column]:
        return filter(None, self._columns)

    @property
    def rows(self):
        return ([self.get_value(row, column) for column in self.columns] for row in self._rows)

    def get_value(self, row, column: Column):
        raise NotImplementedError("get_value() should be implemented by subclasses")

    def get_column(self, column: Column):
        return (row[column._view_index] for row in self.rows)

    def add_column(self, column: Column):
        column = copy.copy(column)
        column._index = next(self._column_counter)
        column._view_index = self._columns[-1]._view_index + 1
        self._columns.append(column)

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

    def get_value(self, row, column: Column):
        value = row[column._index]
        func = column.cellfunc
        return func(value) if func else value


class DictTable(Table):
    def __init__(self, rows: Iterable[dict], columns, lazy=True, size_hint=None):
        """
        @param rows: list of rows
        @param columns: list of columns. The label of a column is used to access dictionary.
        @param lazy: if True, no random access is allowed
        @param size_hint: (approximate) length of rows. Is used by exporters to determine progress.
        """
        super().__init__(rows, columns, lazy=lazy, size_hint=size_hint)

    def get_value(self, row, column: Column):
        value = row[column.label]
        func = column.cellfunc
        return func(value) if func else value


class WrappedTable:
    def __init__(self, table):
        self.table = table

    def __getattr__(self, name):
        return getattr(self.table, name)


class SortedTable(WrappedTable):
    def __init__(self, table, key, reverse=False):
        super(SortedTable, self).__init__(table)
        self.key = key
        self.reverse = reverse
        self.table.to_strict()

    def rows(self):
        return sorted(self.table.rows, key=self.key, reverse=self.reverse)
