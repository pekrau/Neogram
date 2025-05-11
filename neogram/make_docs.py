"Create documentation from JSON Schema."

from icecream import ic

import constants
import schema


TERMS = {"array":"sequence",
         "object": "mapping",
         "number": "float"
         }

def term(v):
    return TERMS.get(v, v)


definitions = {}

INDENT = "  "

def make_docs():
    global definitions

    result = []
    result.append(f"# Neogram {constants.__version__}\n\n")
    result.append(schema.SCHEMA["title"])
    result.append("\n\n")

    result.append("The YAML file must contain the software identification marker:\n\n")
    result.append("    neogram: {version}\n\n")
    result.append(f"where `version` is either `null` or the string representing the version of the software.\n\n")

    if (defs := schema.SCHEMA.get("$defs")):
        for key, value in defs.items():
            if anchor := value.get("$anchor"):
                definitions[anchor] = value

    schema.SCHEMA["properties"].pop("neogram")

    result.append("## Diagrams\n\n")
    for diagram, subschema in schema.SCHEMA["properties"].items():
        result.append(f"- [{diagram}(docs/{diagram}.md): {subschema['title']}\n\n")

    with open("../README.md", "w") as outfile:
        outfile.write("".join(result))

    for diagram, subschema in schema.SCHEMA["properties"].items():
        result = []
        result.append(f"# {diagram}\n")
        href = f"../docs/{diagram}.md"
        result.extend(output_schema(subschema, href=href))
        with open(href, "w") as outfile:
            outfile.write("".join(result) + "\n")


def output_schema(schema, level=0, required=False, href=None):
    global definitions

    result = []
    prefix = INDENT * level

    if level == 0:
        result.append(f"\n{prefix}{schema['title']}\n\n")

    if ref := schema.get("$ref"):
        try:
            schema = definitions[ref[1:]]
            if schema.get("_has_been_output"):
                result.append(f"{prefix}  - *definition*: See elsewhere. {href}\n")
                return result
            schema["_has_been_output"] = True
            schema["_href"] = href
        except KeyError:
            result.append(f"{prefix}- *definition*: See elsewhere.\n")

    if required:
        result.append(f"{prefix}- *required*\n")

    if type := schema.get("type"):
        match type:
            case "object":
                if level != 0:
                    result.append(f"{prefix}- *type*: {term(type)}\n")
                if anchor := schema.get("$anchor"):
                    definitions[anchor] = schema
                    schema["_has_been_output"] = True
                    schema["_href"] = href
                required = set(schema.get("required") or [])
                for key, subschema in schema["properties"].items():
                    if title := subschema.get("title"):
                        result.append(f"{prefix}- **{key}**: {title}\n")
                    else:
                        result.append(f"{prefix}- **{key}**:\n")
                    result.extend(output_schema(subschema, level+1, key in required))
            case "array":
                result.append(f"{prefix}- *type*: {term(type)}\n")
                result.append(f"{prefix}- *items*:\n")
                result.extend(output_schema(schema["items"], level+1))
            case "integer" | "number":
                result.append(f"{prefix}- *type*: {term(type)}\n")
                for constraint in ("minimum", "exclusiveMinimum",
                                   "maximum", "exclusiveMaximum"):
                    try:
                        value = schema[constraint]
                        result.append(f"{prefix}- *{constraint}*: {value}\n")
                    except KeyError:
                        pass
            case _:
                result.append(f"{prefix}- *type*: {term(type)}\n")

    elif enum := schema.get("enum"):
        values = []
        for value in enum:
            if isinstance(value, str):
                value = f"'{value}'"
            values.append(value)
        result.append(f"{prefix}- *one of*: {', '.join(values)}\n")

    elif oneof := schema.get("oneOf"):
        for number, subschema in enumerate(oneof):
            result.append(f"{prefix}- Alternative {number+1}: {subschema['title']}\n")
            result.extend(output_schema(subschema, level+1))

    elif anyof := schema.get("anyOf"):
        for number, subschema in enumerate(anyof):
            result.append(f"{prefix}- Option {number+1}\n")
            result.extend(output_schema(subschema, level+1))

    if (format := schema.get("format")):
        result.append(f"{prefix}- *format*: {format}\n")

    try:
        value = schema["default"]
        if isinstance(value, str):
            value = f"'{value}'"
        elif isinstance(value, bool):
            value = str(value).lower()
        result.append(f"{prefix}- *default*: {value}\n")
    except KeyError:
        pass

    return result


if __name__ == "__main__":
    make_docs()
