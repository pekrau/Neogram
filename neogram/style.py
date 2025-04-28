"Style class."

__all__ = ["Style"]


from color import Color, Palette

STYLE_LABEL_DEFAULTS = dict(
    stroke="none",
    fill=Color("black"),
    font="sans-serif",
    size=14,
    anchor="middle",
    bold=False,
    italic=False,
    underline=False,
)

STYLE_LEGEND_DEFAULTS = STYLE_LABEL_DEFAULTS.copy()
STYLE_LEGEND_DEFAULTS["anchor"] = "start"

STYLE_DEFAULTS = dict(
    stroke=Color("black"),
    stroke_width=1,
    fill=Color("white"),
    radius=10,  # Default depends on the diagram.
    width=10,  # Default depends on the diagram.
    height=10,  # Default depends on the diagram.
    padding=None,  # int
    rounded=None,  # int
    palette=Palette("#4c78a8", "#9ecae9", "#f58518"),
    label=STYLE_LABEL_DEFAULTS,
    legend=STYLE_LEGEND_DEFAULTS,
)

# Defaults for SVG attribute values according to the SVG documentation.
SVG_STYLE_DEFAULTS = {
    "stroke": "none",
    "stroke-width": 1,
    "fill": "black",
    "font-family": None,
    "font-size": None,
    "font-weight": "normal",
    "font-style": "normal",
    "text-anchor": "start",
    "text-decoration": "none",
}

# Translation of Neogram style to SVG attribute name.
SVG_STYLE_ATTRS = {
    "stroke_width": "stroke-width",
    "label.stroke": "stroke",
    "label.stroke_width": "stroke-width",
    "label.fill": "fill",
    "label.font": "font-family",
    "label.size": "font-size",
    "label.anchor": "text-anchor",
    "label.bold": "font-weight",
    "label.italic": "font-style",
    "label.underline": "text-decoration",
    "legend.stroke": "stroke",
    "legen.stroke_width": "stroke-width",
    "legend.fill": "fill",
    "legend.font": "font-family",
    "legend.size": "font-size",
    "legend.anchor": "text-anchor",
    "legend.bold": "font-weight",
    "legend.italic": "font-style",
    "legend.underline": "text-decoration",
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
        case "fill" | "stroke":
            if not isinstance(value, Color):
                value = Color(value)
        case "radius" | "stroke_width" | "size" | "padding" | "rounded":
            if not isinstance(value, (int, float)):
                raise ValueError
            if value <= 0:
                raise ValueError
        case "bold" | "italic" | "underline":
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
        attr = SVG_STYLE_ATTRS.get(key, key)
        # Convert the value according to the SVG attribute.
        match attr:
            case "stroke" | "fill":
                value = "none" if value is None else str(value)
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
        self.set_svg_attribute(elem, f"{kind}.size")
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


if __name__ == "__main__":
    from minixml import Element

    style = Style()
    svg = Element("svg")
    style.push(stroke=Color("red"))
    svg += (g := Element("g"))
    style.set_attribute(g, "stroke")
    style.set_attribute(g, "fill")
    style.set_text_attributes(g, "label")
    g += (text := Element("text"))
    style.set_text_attributes(text, "legend")
    text += "blopp"
    print(repr(svg))
    print(len(style))
