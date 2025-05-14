# note

- [Specification](#specification)
- [Examples](#examples)
  - [declaration](#declaration)
  - [cpies](#cpies)

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
neogram: 0.8.0
note:
  header:
    text: Declaration
    placement: left
  body:
    text: 'This software was

      written by me.'
    placement: right
  footer:
    text: Copyright 2025 Per Kraulis
    italic: true
```
### cpies

![cpies SVG](cpies.svg)

```yaml
neogram: 0.8.0
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

