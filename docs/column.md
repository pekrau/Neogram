# column

- [Specification](#specification)
- [Examples](#examples)
  - [universe_earth](#universe_earth)
  - [cpies](#cpies)

## Specification
Diagrams stacked in a column.

- **title**: Title of the column diagram.
    - *definition*: See [here](timelines.md)
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
## Examples

### universe_earth

![universe_earth SVG](universe_earth.svg)

```yaml
neogram: 0.7.12
column:
  title: Universe and Earth
  entries:
  - timelines:
      title:
        text: Universe
        size: 18
        bold: true
        color: purple
      entries:
      - event:
          label: Big Bang
          timeline: Universe
          color: red
          instant: -13787000000
      - period:
          label: Milky Way galaxy
          timeline: Universe
          color: navy
          begin: -8000000000
          end: 0
      - period:
          label: Earth
          color: lightgreen
          begin: -4567000000
          end: 0
      - event:
          label: Here
          timeline: markers
          instant:
            value: -12000000000
            error: 600000000
          marker: none
      - event:
          label: Circle
          timeline: markers
          color: cyan
          instant: -10000000000
          marker: circle
          placement: left
      - event:
          label: Ellipse
          timeline: markers
          color: blue
          instant: -8000000000
          placement: left
      - event:
          label: ''
          timeline: markers
          color: orange
          instant:
            value: -6000000000
            low: -6500000000
            high: -5000000000
          marker: square
      - event:
          label: Pyramid
          timeline: markers
          color: gold
          instant: -4000000000
          marker: pyramid
          placement: center
      - event:
          label: Triangle
          timeline: markers
          color: purple
          instant: -2000000000
          marker: triangle
  - timelines:
      title: Earth
      entries:
      - period:
          label: Earth
          begin: -4567000000
          end: 0
      - period:
          label: Archean
          color: lime
          begin:
            value: -4000000000
            low: -4100000000
            high: -3950000000
          end:
            value: -2500000000
            error: 200000000
          fuzzy_marker: gradient
      - event:
          label: LUCA?
          timeline: Unicellular
          instant: -4200000000
      - period:
          label: Unicellular organisms
          timeline: Unicellular
          begin:
            value: -3480000000
            low: -4200000000
          end: 0
          fuzzy_marker: gradient
      - period:
          label: Eukaryotes
          begin: -1650000000
          end: 0
      - period:
          label: Photosynthesis
          begin: -3400000000
          end: 0
      - period:
          label: Plants
          timeline: Photosynthesis
          begin: -470000000
          end: 0
```
### cpies

![cpies SVG](cpies.svg)

```yaml
neogram: 0.7.12
column:
  title: Pies in column
  entries:
  - piechart:
      title: Strawberry pie
      entries:
      - slice:
          label: Flour
          value: 7
          color: white
      - slice:
          label: Eggs
          value: 2
          color: yellow
      - slice:
          label: Butter
          value: 3
          color: gold
      - slice:
          label: Strawberries
          value: 3
          color: orangered
      diameter: 100
  - piechart:
      title: Rhubarb pie
      entries:
      - slice:
          label: Flour
          value: 7
          color: white
      - slice:
          label: Eggs
          value: 2
          color: yellow
      - slice:
          label: Butter
          value: 3
          color: gold
      - slice:
          label: Rhubarb
          value: 3
          color: green
```

