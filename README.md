# AmCATable
`amcatable` aims to make it easy to export all kinds of data to various formats. There is a focus on lazyness, speed, and a low memory footprint. Currently, it supports the following formats:

* SPSS (sav)
* ~~R (rda)~~
* Excel (xlsx, xls)
* Text (csv, ~~latex~~, ~~html~~)

All tables are exportable to Django streaming responses as well, making it easy to integrate into your existing web projects.

## Basic examples
The examples below (unless specified otherwise) assume the followig code prepending it:

```python
from amcattable import ListTable, columns

table = ListTable(
    columns=[
        columns.IntColumn("h1"),
        columns.FloatColumn("h2"),
        columns.TextColumn("h3"),
        columns.DateTimeColumn("h4")
    ]
    rows=[
        [1, 2.1, "foo", datetime.datetime(2010, 11, 2, 1, 1)],
        [3, 4.2, "bar", datetime.datetime(2011, 12, 3, 2, 9)],
    ]
)
```

Notice that each column has a type and a label associated with it. 

### Dump to stream
Implicitly select an exporter using a file extension:

```python
>>> my_file = open("myfile.xlsx", "wb")
>>> table.dump(my_file, "xlsx")
```

Explicitly select an exporter by importing it:

```python
>>> from amcatable.exporters import XLSXEporter
>>> my_file = open("myfile.xlsx", "wb")
>>> table.dump(my_file, XLSXExporter())
```

### Dump to bytes
Simply changing `dump` to `dumps` allows you to dump to a string of bytes:

```python
>>> type(table.dumps("xlsx"))
<class 'bytes'>
```

### Render as Django Streaming Response


### Declared tables

## Advanced usage
TODO
