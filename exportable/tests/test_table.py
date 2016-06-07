###########################################################################
#          (C) Vrije Universiteit, Amsterdam (the Netherlands)            #
#                                                                         #
# This file is part of AmCAT - The Amsterdam Content Analysis Toolkit     #
#                                                                         #
# AmCAT is free software: you can redistribute it and/or modify it under  #
# the terms of the GNU Affero General Public License as published by the  #
# Free Software Foundation, either version 3 of the License, or (at your  #
# option) any later version.                                              #
#                                                                         #
# AmCAT is distributed in the hope that it will be useful, but WITHOUT    #
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or   #
# FITNESS FOR A PARTICULAR PURPOSE. See the GNU Affero General Public     #
# License for more details.                                               #
#                                                                         #
# You should have received a copy of the GNU Affero General Public        #
# License along with AmCAT.  If not, see <http://www.gnu.org/licenses/>.  #
###########################################################################
import unittest

from exportable.columns import IntColumn
from exportable.table import ListTable


class TestListTable(unittest.TestCase):
    def test_simple(self):
        """Very simple test case to cover the basics"""
        columns = [IntColumn("A"), IntColumn("B")]
        rows = [[1, 2], [3, 4]]
        table = ListTable(columns=columns, rows=rows)
        self.assertEqual(rows, list(table.rows))

    def test_missing(self):
        """Row items should be skipped if column is None"""
        columns = [None, IntColumn("B")]
        rows = [[1, 2], [3, 4]]
        table = ListTable(columns=columns, rows=rows)
        self.assertEqual([[2], [4]], list(table.rows))

    def test_predefined_rowfuncs(self):
        """Table should not override rowfunc if supplied by user"""
        columns = [IntColumn("A", rowfunc=lambda row: 9), IntColumn("B")]
        rows = [[1, 2], [3, 4]]
        table = ListTable(columns=columns, rows=rows)
        self.assertEqual([[9, 2], [9, 4]], list(table.rows))

    def test_add_column_simple(self):
        """add_column should behave the same as giving columns upfront"""
        columns = [IntColumn("A"), IntColumn("B")]
        table = ListTable(rows=[[1, 2], [3, 4]])
        for column in columns:
            table.add_column(column)
        self.assertEqual([[1, 2], [3, 4]], list(table.rows))

    def test_add_column_missing(self):
        """add_column should behave the same as giving columns upfront"""
        columns = [None, IntColumn("B")]
        rows = [[1, 2], [3, 4]]
        table = ListTable(rows=rows)
        for column in columns:
            table.add_column(column)
        self.assertEqual([[2], [4]], list(table.rows))

    def test_add_column_predefined_rowfuncs(self):
        """add_column should behave the same as giving columns upfront"""
        columns = [IntColumn("A", rowfunc=lambda row: 9), IntColumn("B")]
        table = ListTable(rows=[[1, 2], [3, 4]])
        for column in columns:
            table.add_column(column)
        self.assertEqual([[9, 2], [9, 4]], list(table.rows))


class TestDictTable(unittest.TestCase):
    pass


class TestAttributeTable(unittest.TestCase):
    pass
