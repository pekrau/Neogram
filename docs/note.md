# note

- [Specification](#specification)
- [Examples](#examples)
  - [declaration](#declaration)
  - [cpies](#cpies)
  - [poster](#poster)

## Specification
Textual note with header, body and footer text.

- **header**: Header of the note.
    - *definition*: See [here](timelines.md)
- **body**: Body of the note.
    - *definition*: See [here](timelines.md)
- **footer**: Footer of the note.
    - *definition*: See [here](timelines.md)
- **width**: Width of chart, in pixels.
  - *type*: float
  - *exclusiveMinimum*: 0
  - *default*: 200
- **frame**: Thickness of the frame.
  - *type*: float
  - *minimum*: 0
  - *default*: 5
- **color**: Color of the note frame and lines.
  - *type*: string
  - *format*: color
  - *default*: 'gold'
- **radius**: Radius of the frame edge curvature.
  - *type*: float
  - *minimum*: 0
  - *default*: 10
- **line**: Thickness of lines between sections.
  - *type*: float
  - *minimum*: 0
  - *default*: 1
- **background**: Background color of the note.
  - *type*: string
  - *format*: color
  - *default*: 'lightyellow'
## Examples

### declaration

![declaration SVG](declaration.svg)

```yaml
neogram: 0.8.1
board:
  entries:
  - x: 0
    y: 0
    scale: 1.5
    column:
      entries:
      - note:
          header:
            text: Declaration
            placement: left
            bold: true
          body:
            text: 'This software was

              written by me.'
            placement: right
          footer:
            text: Copyright 2025 Per Kraulis
            italic: true
      - note:
          header: Header
          body: Body
          footer: Footer
      - note:
          header: Header
          body: Body
      - note:
          body: Body
          footer: Footer
      - note:
          header: Header
      - note:
          body: Body
      - note:
          footer: Footer
      - note:
          header: Header
          body: Body
          footer: Footer
          line: 0
```
### cpies

![cpies SVG](cpies.svg)

```yaml
neogram: 0.8.1
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
  - note:
      header: Comment
      body: Strawberry pie is good.
      footer:
        text: Copyright 2025 Per Kraulis
        italic: true
```
### poster

![poster SVG](poster.svg)

```yaml
neogram: 0.8.1
board:
  title: Poster
  entries:
  - x: 250
    y: 10
    note:
      header: By Per Kraulis
      body: Ph.D.
      footer: Stockholm University
  - x: 0
    y: 100
    timelines:
      title:
        text: Universe
        bold: true
        color: blue
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
          begin:
            value: -7500000000
            low: -8500000000
          end: 0
          fuzzy: gradient
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
          placement: center
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
  - x: 50
    y: 230
    timelines:
      title: Earth
      entries:
      - period:
          label: Earth
          begin: -4567000000
          end: 0
      - period:
          label: Archean
          color: wheat
          begin:
            value: -4000000000
            low: -4100000000
            high: -3950000000
          end:
            value: -2500000000
            error: 200000000
          fuzzy: gradient
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
          fuzzy: gradient
      - period:
          label: Eukaryotes
          begin: -1650000000
          end: 0
      - period:
          label: Engineers
          color: lightgray
          begin:
            value: -3300000000
            error: 200000000
          end: -1650000000
          fuzzy: wedge
      - period:
          label: Photosynthesis
          color: springgreen
          begin: -3400000000
          end: 0
      - period:
          label: Plants
          timeline: Photosynthesis
          color: green
          begin: -470000000
          end: 0
          placement: left
```

