# Neogram 0.8.2

Generate SVG for diagrams of different kinds from YAML specification.

The YAML file must contain the software identification marker:

    neogram: {version}

where `{version}` is either `null` or the string representing the version of the software.

The full JSON Schema is [here](docs/schema.json).

## Diagrams

- [timelines](docs/timelines.md): Timelines having events and periods.

- [piechart](docs/piechart.md): Pie chart containing slices.

- [column](docs/column.md): Diagrams stacked in a column.

- [row](docs/row.md): Diagrams arranged in a row.

- [note](docs/note.md): Textual note with header, body and footer text.

- [board](docs/board.md):  "Diagram to place diagrams at specified positions.
    Cannot be used in other diagrams.
    

