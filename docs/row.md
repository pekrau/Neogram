# row

Diagrams arranged in a row.

- **title**:
    - *definition*: See [here](timelines.md)
- **align**: Align diagrams vertically within the row.
  - *one of*: 'bottom', 'center', 'top'
  - *default*: 'center'
- **entries**: Component diagrams in the row.
  - *type*: sequence
  - *items*:
    - *type*: mapping
    - **timelines**:
        - *definition*: See [here](timelines.md)
    - **piechart**:
        - *definition*: See [here](piechart.md)
    - **column**:
        - *definition*: See [here](column.md)
    - **row**:
        - *definition*: See [here](row.md)

