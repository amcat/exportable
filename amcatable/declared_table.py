import functools

from amcatable.columns import Column
from amcatable.table import WrappedTable


def get_columns(cls):
    for attr_name in dir(cls):
        if not attr_name.startswith("_"):
            column = getattr(cls, attr_name)
            if isinstance(column, Column):
                if column.label is None:
                    column.label = attr_name
                yield column


class DeclaredTable(WrappedTable):
    def __init__(self, table_cls, rows, lazy=True, size_hint=None):
        columns = self.__class__._get_columns()
        super().__init__(table_cls(rows, columns, lazy=lazy, size_hint=size_hint))

    @classmethod
    @functools.lru_cache()
    def _get_columns(cls):
        return tuple(sorted(get_columns(cls), key=lambda c: c._creation_counter))

