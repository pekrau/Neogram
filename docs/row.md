# row

- [Specification](#specification)
- [Examples](#examples)
  - [rpies](#rpies)

## Specification
Diagrams arranged in a row.

- **title**: Title of the column diagram.
    - *definition*: See [here](timelines.md)
- **align**: Align diagrams vertically within the row.
  - *one of*: 'bottom', 'middle', 'top'
  - *default*: 'middle'
- **entries**: Component diagrams in the row.
  - *required*
  - *type*: sequence
  - *items*:
    - *type*: mapping
    - **timelines**:
        - *definition*: See [here](column.md)
    - **piechart**:
        - *definition*: See [here](column.md)
    - **note**:
        - *definition*: See [here](column.md)
    - **column**:
        - *definition*: See [here](column.md)
    - **row**:
        - *definition*: See [here](column.md)
## Examples

### rpies

![rpies SVG](rpies.svg)

```yaml
neogram: 0.8.2
row:
  title: Pies in row
  entries:
  - piechart:
      title: Strawberry pie
      entries:
      - slice:
          label: Flour
          value: 7
      - slice:
          label: Eggs
          value: 2
      - slice:
          label: Butter
          value: 3
      - slice:
          label: Strawberries
          value: 3
      diameter: 300
      palette:
      - white
      - yellow
      - gold
      - red
  - piechart:
      title: Rhubarb pie
      entries:
      - slice:
          label: Flour
          value: 7
      - slice:
          label: Eggs
          value: 2
      - slice:
          label: Butter
          value: 3
      - slice:
          label: Rhubarb
          value: 3
          color: green
      palette:
      - white
      - yellow
      - gold
      - red
```

