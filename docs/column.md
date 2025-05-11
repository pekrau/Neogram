# column

Diagrams stacked in a column.

- **title**:
    - *definition*: See [here](None)
- **align**: Align diagrams horizontally within the column.
  - *one of*: 'left', 'center', 'right'
  - *default*: 'center'
- **entries**: Component diagrams in the column.
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
      - *definition*: See elsewhere.

