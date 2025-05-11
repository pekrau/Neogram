# Neogram 0.7.8

YAML specification for diagrams of different kinds.

The YAML file must contain the software identification marker:

    neogram: version

where `version` is either `null` or the version of the software.

## timelines

Timelines having events and periods.

- **title**:
  - Alternative 1: Title of the diagram with default styling.
    - *type*: string
  - Alternative 2: Title of the diagram with styling options.
    - *type*: mapping
    - **text**: Text of title.
      - *required*
      - *type*: string
    - **size**: Size of font in title.
      - *type*: float
      - *exclusiveMinimum*: 0
    - **bold**: Text in bold.
      - *type*: boolean
      - *default*: false
    - **italic**: Text in italics.
      - *type*: boolean
      - *default*: false
    - **color**: Color of text.
      - *type*: string
      - *format*: color
      - *default*: 'black'
    - **anchor**: Anchor of title text.
      - enum:
        - 'start'
        - 'middle'
        - 'end'
      - *default*: 'middle'
- **width**: Width of chart, in pixels.
  - *type*: float
  - *exclusiveMinimum*: 0
  - *default*: 600
- **legend**: Display legend.
  - *type*: boolean
  - *default*: true
- **entries**: Entries in the timelines.
  - *items*:
    - Option 1
      - *type*: mapping
      - **event**: Event at a moment in time.
        - *type*: mapping
        - **label**:
          - *required*
          - *type*: string
        - **moment**:
          - *required*
          - *type*: float
        - **timeline**:
          - *type*: string
        - **color**:
          - *type*: string
          - *format*: color
    - Option 2
      - *type*: mapping
      - **period**: Period of time.
        - *type*: mapping
        - **label**:
          - *required*
          - *type*: string
        - **begin**:
          - *required*
          - *type*: float
        - **end**:
          - *required*
          - *type*: float
        - **timeline**:
          - *type*: string
        - **color**:
          - *type*: string
          - *format*: color

## piechart

Pie chart containing slices.

- **title**:
    - *definition*: See elsewhere.
- **diameter**: Diameter of the pie chart, in pixels.
  - *type*: float
  - *exclusiveMinimum*: 0
  - *default*: 200
- **total**: Total value to relate slice values to.
  - *type*: float
  - *exclusiveMinimum*: 0
- **start**: Starting point for first slice; in degrees from top.
  - *type*: float
- **entries**: Entries (slices) in the pie chart.
  - *items*:
    - *type*: mapping
    - **slice**: Slice representing a value.
      - *type*: mapping
      - **label**:
        - *required*
        - *type*: string
      - **value**:
        - *required*
        - *type*: float
      - **color**:
        - *type*: string
        - *format*: color

## column

Diagrams stacked in a column.

- **title**:
    - *definition*: See elsewhere.
- **align**: Align diagrams horizontally within the column.
  - enum:
    - 'left'
    - 'center'
    - 'right'
  - *default*: 'center'
- **entries**: Component diagrams in the column.
  - *items*:
    - *type*: mapping
    - **timelines**:
        - *definition*: See elsewhere.
    - **piechart**:
        - *definition*: See elsewhere.
    - **column**:
        - *definition*: See elsewhere.
    - **row**:
      - *definition*: See elsewhere.

## row

Diagrams arranged in a row.

- **title**:
    - *definition*: See elsewhere.
- **align**: Align diagrams vertically within the row.
  - enum:
    - 'bottom'
    - 'center'
    - 'top'
  - *default*: 'center'
- **entries**: Component diagrams in the row.
  - *items*:
    - *type*: mapping
    - **timelines**:
        - *definition*: See elsewhere.
    - **piechart**:
        - *definition*: See elsewhere.
    - **column**:
        - *definition*: See elsewhere.
    - **row**:
        - *definition*: See elsewhere.

