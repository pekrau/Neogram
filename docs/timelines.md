# timelines

- [Specification](#specification)
- [Examples](#examples)
  - [universe](#universe)
  - [earth](#earth)
  - [universe_earth](#universe_earth)

## Specification
Timelines having events and periods.

- **title**: Title of the timelines diagram.
  - Alternative 1: Text with default styling.
    - *type*: string
  - Alternative 2: Text with styling options.
    - *type*: mapping
    - **text**: The text to display.
      - *required*
      - *type*: string
    - **size**: Size of font.
      - *type*: float
      - *exclusiveMinimum*: 0
    - **bold**: Bold font.
      - *type*: boolean
      - *default*: false
    - **italic**: Italics font.
      - *type*: boolean
      - *default*: false
    - **color**: Color of text.
      - *type*: string
      - *format*: color
      - *default*: 'black'
    - **anchor**: Anchor of text.
      - *one of*: 'start', 'middle', 'end'
      - *default*: 'middle'
- **width**: Width of chart, in pixels.
  - *type*: float
  - *exclusiveMinimum*: 0
  - *default*: 600
- **legend**: Display legend.
  - *type*: boolean
  - *default*: true
- **axis**: Time axis specification.
  - Alternative 1: Display default time axis.
    - *type*: boolean
    - *default*: true
  - Alternative 2: Time axis details.
    - *type*: mapping
    - **absolute**: Display absolute values for ticks.
      - *type*: boolean
      - *default*: false
    - **color**: Color of tick lines.
      - *type*: string
      - *format*: color
      - *default*: 'gray'
    - **caption**: Time axis description.
      - *type*: string
- **entries**: Entries in the timelines.
  - *type*: sequence
  - *items*:
    - Option 1
      - *type*: mapping
      - **event**: Event at an instant in time.
        - *type*: mapping
        - **label**: Description of the event.
          - *required*
          - *type*: string
        - **instant**: Time of the event.
          - *required*
          - Alternative 1: Exact time.
            - *type*: float
          - Alternative 2: Imprecise time.
            - *type*: mapping
            - **value**: Central value for the fuzzy number.
              - *required*
              - *type*: float
            - **low**: Low value for the fuzzy number.
              - *type*: float
            - **high**: High value for the fuzzy number.
              - *type*: float
            - **error**: Symmetrical error around the central value.
              - *type*: float
              - *exclusiveMinimum*: 0
        - **timeline**: Timeline to place the event in.
          - *type*: string
        - **marker**: Marker for event.
          - *one of*: 'circle', 'ellipse', 'square', 'pyramid', 'triangle', 'none'
          - *default*: 'ellipse'
        - **color**: Color of the event marker.
          - *type*: string
          - *format*: color
          - *default*: 'black'
        - **placement**: Placement of event label.
          - *one of*: 'left', 'center', 'right'
        - **fuzzy**: Use error bar marker for fuzzy number.
          - *type*: boolean
          - *default*: true
    - Option 2
      - *type*: mapping
      - **period**: Period of time.
        - *type*: mapping
        - **label**: Description of the period.
          - *required*
          - *type*: string
        - **begin**: Starting time of the period.
          - *required*
          - Alternative 1: Exact time.
            - *type*: float
          - Alternative 2: Imprecise time.
              - *definition*: See [here](timelines.md)
        - **end**: Ending time of the period.
          - *required*
          - Alternative 1: Exact time.
            - *type*: float
          - Alternative 2: Imprecise time.
              - *definition*: See [here](timelines.md)
        - **timeline**: Timeline to place the period in.
          - *type*: string
        - **color**: Color of the period graphic.
          - *type*: string
          - *format*: color
          - *default*: 'white'
        - **fuzzy**: Marker to use for fuzzy number.
          - *one of*: 'error', 'wedge', 'gradient', 'none'
          - *default*: 'error'
## Examples

### universe

![universe SVG](universe.svg)

```yaml
neogram: 0.7.13
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
```
### earth

![earth SVG](earth.svg)

```yaml
neogram: 0.7.13
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
```
### universe_earth

![universe_earth SVG](universe_earth.svg)

```yaml
neogram: 0.7.13
column:
  title: Universe and Earth
  entries:
  - timelines:
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
      legend: false
  - timelines:
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
      legend: false
```

