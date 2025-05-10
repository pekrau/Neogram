"Convert Neogram YAML file to SVG."

import pathlib
import sys

import click

import lib


@click.command()
@click.option("-i", "--indent", default=2, type=int)
@click.argument("infilepath", nargs=1, required=True)
@click.argument("outfilepath", nargs=1, required=False)
def tosvg(indent, infilepath, outfilepath):
    infilepath = pathlib.Path(infilepath)
    if not infilepath.exists():
        raise click.BadParameter("no such input file")
    try:
        diagram = lib.retrieve(infilepath)
    except ValueError as error:
        sys.exit(f"Error: {error}")
    if not outfilepath:
        outfilepath = infilepath.with_suffix(".svg")
    diagram.render(outfilepath, indent=max(0, indent))


if __name__ == "__main__":
    tosvg()
