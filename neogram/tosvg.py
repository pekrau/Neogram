"Neogram: Convert YAML file to SVG."

import pathlib

import click

from diagrams import retrieve


@click.command()
@click.option("-i", "--indent", default=2, type=int)
@click.argument("infilepath", nargs=1, required=True)
@click.argument("outfilepath", nargs=1, required=False)
def tosvg(indent, infilepath, outfilepath):
    infilepath = pathlib.Path(infilepath)
    if not infilepath.exists():
        raise click.BadParameter("no such input file")
    diagram = retrieve(infilepath)
    if not outfilepath:
        outfilepath = infilepath.with_suffix(".svg")
    with open(outfilepath, "w") as outfile:
        diagram.svg_document().write(outfile, indent=max(0, indent))
    

if __name__ == "__main__":
    tosvg()
