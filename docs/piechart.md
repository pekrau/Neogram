# piechart

Pie chart containing slices.

- **title**:
    - *definition*: See [here](timelines.md)
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
  - *type*: sequence
  - *items*:
    - *type*: mapping
    - **slice**: Slice representing a value.
      - *type*: mapping
      - **label**: Description of the value.
        - *required*
        - *type*: string
      - **value**: The value represented by the slice.
        - *required*
        - *type*: float
        - *exclusiveMinimum*: 0
      - **color**: Color of the slice. Use palette if not defined.
        - *type*: string
        - *format*: color

