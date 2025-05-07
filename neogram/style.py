"Style handling."

from color import Color, Palette

STYLE_TEXT_DEFAULTS = dict(
    width=True,
    stroke=None,
    fill=Color("black"),
    font="sans-serif",
    font_size=14,
    descend=2,
    anchor=None,
    bold=False,
    italic=False,
    underline=False,
    contrast=False,
)

STYLE_AXIS_DEFAULTS = dict(
    stroke=Color("black"),
    stroke_width=1,
    number=8,
    labels=True,
    absolute=False,
)

STYLE_DEFAULTS = dict(
    stroke=Color("black"),
    stroke_width=1,
    fill=Color("white"),
    width=0,  # Default depends on the diagram.
    height=0,  # Default depends on the diagram.
    size=0,  # Default depends on the diagram.
    start=0,
    padding=0,
    rounded=0,
    palette=Palette("#4c78a8", "#9ecae9", "#f58518"),
    title=STYLE_TEXT_DEFAULTS,
    label=STYLE_TEXT_DEFAULTS,
    legend=STYLE_TEXT_DEFAULTS,
    axis=STYLE_AXIS_DEFAULTS,
)

# Defaults for SVG attribute values according to the SVG documentation.
SVG_STYLE_DEFAULTS = {
    "stroke": None,
    "stroke-width": 1,
    "fill": "black",
    "font-family": None,
    "font-size": None,
    "font-weight": "normal",
    "font-style": "normal",
    "text-anchor": "start",
    "text-decoration": None,
}

# Translation of Neogram style name to SVG attribute name.
SVG_STYLE_ATTRS = {
    "stroke_width": "stroke-width",
    "font": "font-family",
    "font_size": "font-size",
    "anchor": "text-anchor",
    "bold": "font-weight",
    "italic": "font-style",
    "underline": "text-decoration",
}


def stylify(styles):
    """Convert (and check) each value in the provided unflattened dictionary
    to the proper representation according to the key.
    """
    result = {}
    if styles is None:
        return result
    try:
        for key, value in list(styles.items()):
            if isinstance(value, dict):
                result[key] = stylify(value)
            elif value is not None:
                result[key] = to_style_value(key, value)
    except ValueError:
        raise ValueError(f"invalid value for '{key}': {value}")
    return result


def to_style_value(key, value):
    "Convert (and check) the value to the proper representation according to the key."
    assert value is not None
    match key:
        # Color value.
        case "fill" | "stroke":
            if not isinstance(value, Color):
                value = Color(value)

        # Positive int or float.
        case "radius" | "stroke_width" | "font_size" | "number":
            if not isinstance(value, (int, float)):
                raise ValueError
            if value <= 0:
                raise ValueError

        # Non-negative int or float.
        case "descend" | "padding" | "rounded":
            if not isinstance(value, (int, float)):
                raise ValueError
            if value < 0:
                raise ValueError

        # Boolean value.
        case "bold" | "italic" | "underline" | "contrast" | "labels" | "absolute":
            value = bool(value)
    return value


def destylify(styles):
    "Reverse of stylify; for YAML output."
    result = {}
    if styles is None:
        return result
    for key, value in styles.items():
        match value:
            case Color():
                result[key] = str(value)
            case Palette():
                result[key] = [str(c) for c in value]
            case dict():
                result[key] = destylify(value)
            case _:
                result[key] = value
    return result


class Style:
    "Style specifications stack."

    def __init__(self, **kwargs):
        self.stack = [self._flatten(None, STYLE_DEFAULTS)]  # This creates a copy.
        data = stylify(kwargs)
        for key, value in self._flatten(None, data).items():
            self[key] = value

    def _flatten(self, prefix, data):
        assert prefix is None or isinstance(prefix, str)
        assert isinstance(data, dict)
        result = {}
        for key, value in data.items():
            fullkey = key if prefix is None else f"{prefix}.{key}"
            if isinstance(value, dict):
                result.update(self._flatten(fullkey, value))
            else:
                result[fullkey] = value
        return result

    def _unflatten(self, data):
        assert isinstance(data, dict)
        result = {}
        for key, value in data.items():
            parts = key.split(".")
            subresult = result
            for part in parts[:-1]:
                subresult = subresult.setdefault(part, {})
            subresult[parts[-1]] = value
        return result

    def __len__(self):
        return len(self.stack)

    def __getitem__(self, key):
        "Get the value for the style, searching from the top of the stack."
        for style in reversed(self.stack):
            try:
                return style[key]
            except KeyError:
                pass
        raise KeyError(f"no such style '{key}'")

    def __setitem__(self, key, value):
        "Set the value of the style at the top of the stack given the flattened key."
        if key not in self.stack[0]:
            raise KeyError(f"no such style '{key}'")
        self.stack[-1][key] = to_style_value(key.split(".")[-1], value)

    def __enter__(self):
        "Push the style stack."
        self.stack.append({})
        self.svg_stack.append(self.svg_stack[-1].copy())
        return self

    def __exit__(self, type, value, tb):
        "Pop the style stack."
        self.stack.pop()
        self.svg_stack.pop()
        return False

    def __contains__(self, key):
        "Is the given key in the top of the stack?"
        return key in self.stack[-1]

    def set_default(self, key, value):
        "Set the default value for the given key, if not already set."
        assert len(self.stack) == 1
        if key not in self.stack[0]:
            raise KeyError(f"no such style '{key}'")
        if not self.stack[0][key]:  # Zero, if not set explicitly.
            self.stack[0][key] = to_style_value(key, value)

    def update(self, data):
        "Modify the stack top according to the data dictionary."
        assert data is None or isinstance(data, dict)
        data = stylify(data)
        flattened = self._flatten(None, data)
        for key in list(flattened):
            if key not in self.stack[0]:
                raise KeyError(f"no such style '{key}'")
        self.stack[-1].update(flattened)

    def init_svg_attributes(self):
        "Initialize the SVG output attributes stack."
        self.svg_stack = [SVG_STYLE_DEFAULTS.copy()]

    def set_svg_attribute(self, elem, key, value=None):
        """Set the given style as SVG attribute in the given element.
        If the SVG attribute's value has not changed, then do nothing.
        """
        if value is None:
            value = self[key]
        # Convert the key from Neogram to SVG terminology.
        attr = key.split(".")[-1]
        try:
            attr = SVG_STYLE_ATTRS[attr]
        except KeyError:
            pass
        # Convert the value according to the SVG attribute.
        # Not all values need to be converted.
        match attr:
            case "stroke" | "fill":
                value = str(value) if value else "none"
            case "font-weight":
                value = "bold" if value else "normal"
            case "font-style":
                value = "italic" if value else "normal"
            case "text-decoration":
                value = "underline" if value else "none"
        if value != self.svg_stack[-1][attr]:
            elem[attr] = value
            self.svg_stack[-1][attr] = value

    def set_svg_text_attributes(self, elem, kind):
        """Set the styles applicable to SVG text elements.
        If the attribute's value has not changed, then do nothing.
        """
        self.set_svg_attribute(elem, f"{kind}.stroke")
        self.set_svg_attribute(elem, f"{kind}.fill")
        self.set_svg_attribute(elem, f"{kind}.font")
        self.set_svg_attribute(elem, f"{kind}.font_size")
        # Special case for legend; default anchor is 'start'.
        if self[f"{kind}.anchor"] is None:
            if kind == "legend":
                self.set_svg_attribute(elem, "legend.anchor", value="start")
            else:
                self.set_svg_attribute(elem, f"{kind}.anchor", value="middle")
        else:
            self.set_svg_attribute(elem, f"{kind}.anchor")
        self.set_svg_attribute(elem, f"{kind}.bold")
        self.set_svg_attribute(elem, f"{kind}.italic")
        self.set_svg_attribute(elem, f"{kind}.underline")

    def as_dict(self):
        """Return as a dictionary of basic YAML values.
        Only return values that are different in the top of the stack.
        """
        data = self.as_dict_content()
        if data:
            return {"style": destylify(data)}
        else:
            return {}

    def as_dict_content(self):
        """Return the content as a dictionary of basic YAML values.
        Only return values that have been set at the top of the stack.
        """
        if len(self.stack) == 1:
            result = {}
            for key, value in self._flatten(None, STYLE_DEFAULTS).items():
                if (new := self.stack[0][key]) != value:
                    result[key] = new
        else:
            result = self.stack[-1]
        return self._unflatten(destylify(result))


STROKE_SCHEMA = {
    "title": "Color for outline, line and curve",
    "oneOf": [
        {"type": "string", "format": "color"},
        {"const": None},
    ],
}

STROKE_WIDTH_SCHEMA = {
    "title": "Width of outline, line and curve",
    "type": "number",
    "minimum": 0,
}

FILL_SCHEMA = {
    "title": "Color for area.",
    "oneOf": [
        {"type": "string", "format": "color"},
        {"const": None},
    ],
}

TEXT_SCHEMA = {
    "type": "object",
    "properties": {
        "width": {
            "oneOf": [
                {
                    "title": "Width of text area.",
                    "type": "number",
                    "minimum": 2,
                },
                {
                    "title": "Compute width of text area, or do not display.",
                    "type": "boolean",
                },
            ],
        },
        "stroke": STROKE_SCHEMA,
        "fill": FILL_SCHEMA,
        "font": {
            "title": "Name of font family.",
            "type": "string",
        },
        "font_size": {
            "title": "Size of the font.",
            "type": "number",
            "exclusiveMinimum": 0,
        },
        "descend": {
            "title": "Size of the font descender.",
            "type": "number",
            "minimum": 0,
        },
        "anchor": {
            "title": "Placement point for the output string.",
            "enum": ["start", "middle", "end"],
        },
        "bold": {
            "title": "Bold text or normal.",
            "type": "boolean",
            "default": False,
        },
        "italic": {
            "title": "Italic text or normal.",
            "type": "boolean",
            "default": False,
        },
        "underline": {
            "title": "Underlined text or normal.",
            "type": "boolean",
            "default": False,
        },
        "contrast": {
            "title": "Set to white or black for best contrast against background.",
            "type": "boolean",
            "default": False,
        },
    },
    "additionalProperties": False,
}

SCHEMA = {
    "title": "Style",
    "description": "Style specification",
    "type": "object",
    "properties": {
        "stroke": STROKE_SCHEMA,
        "stroke_width": STROKE_WIDTH_SCHEMA,
        "fill": FILL_SCHEMA,
        "width": {
            "title": "Width of diagram, if applicable.",
            "type": "number",
            "minimum": 0,
        },
        "height": {
            "title": "Height of diagram, if applicable.",
            "type": "number",
            "minimum": 0,
        },
        "size": {
            "title": "Size of main graphical items of the specific diagram.",
            "type": "number",
            "minimum": 0,
        },
        "start": {
            "title": "Start of graphical items.",
            "type": "number",
            "minimum": 0,
        },
        "padding": {
            "title": "Padding around main graphical items of the specific diagram.",
            "type": "number",
            "minimum": 0,
        },
        "rounded": {
            "title": "Rounding of the main rectangle items of the specific diagram.",
            "type": "number",
            "minimum": 0,
        },
        "palette": {
            "title": "Color palette for graphical items to cycle through.",
            "type": "array",
            "items": {
                "type": "string",
                "format": "color",
            },
        },
        "label": {"$ref": "#/$defs/text"},
        "legend": {"$ref": "#/$defs/text"},
        "axis": {
            "type": "object",
            "properties": {
                "stroke": STROKE_SCHEMA,
                "stroke_width": STROKE_WIDTH_SCHEMA,
                "number": {"title": "Requested number of ticks.", "type": "integer"},
                "labels": {"title": "Display labels for values.", "type": "boolean"},
                "absolute": {
                    "title": "Display absolute values of label values.",
                    "type": "boolean",
                },
                "additionalProperties": False,
            },
        },
        "additionalProperties": False,
    },
    "additionalProperties": False,
}
