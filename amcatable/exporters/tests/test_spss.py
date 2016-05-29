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
import string
import time
import datetime
import unittest

from amcatable.columns import IntColumn, DateTimeColumn, TextColumn
from amcatable.exporters import SPSSExporter
from amcatable.table import ListTable

class Timer:
    def __enter__(self):
        self.start = time.clock()
        return self

    def __exit__(self, *args):
        self.end = time.clock()
        self.interval = self.end - self.start


class TestSPSSExporter(unittest.TestCase):
    def test_simple_table(self):
        rows = (
            [1, None, 3, datetime.datetime.now(), ((string.ascii_lowercase)*2)]
            for _ in range(100000)
        )

        table = ListTable(size_hint=100000, rows=rows, columns=[
                    IntColumn("a"), IntColumn("b"),
                    IntColumn("c"), DateTimeColumn("d"),
                    TextColumn("e")
                ]
            )

        target = open("/dev/null", "wb")
        with Timer() as t:
            table.dump(target, SPSSExporter())
