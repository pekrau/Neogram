"Neogram: Command line tool to convert YAML file to SVG or PNG."

import pathlib

import click

from piechart import *
from gantt import *


@click.group()
def cli():
    pass


@cli.command()
@click.option("-i", "--indent", default=2, type=int)
@click.argument("infilepath", nargs=1, required=True)
@click.argument("outfilepath", nargs=1, required=False)
def svg(indent, infilepath, outfilepath=None):
    "Convert Neogram YAML to SVG file."
    chart = read(infilepath)
    if not outfilepath:
        outfilepath = pathlib.Path(infilepath).with_suffix(".svg")
    with open(outfilepath, "w") as outfile:
        chart.svg().write(outfile, indent=max(0, indent))


def validate_scale(ctx, param, value):
    if value <= 0.0:
        raise click.BadParameter("scale must be larger than 0.0")
    return value


@cli.command()
@click.option("-s", "--scale", default=1.0, type=float, callback=validate_scale)
@click.argument("infilepath", nargs=1, required=True)
@click.argument("outfilepath", nargs=1, required=False)
def png(scale, infilepath, outfilepath=None):
    "Convert Neogram YAML to PNG file."
    chart = read(infilepath)
    if not outfilepath:
        outfilepath = pathlib.Path(infilepath).with_suffix(".png")
    with open(outfilepath, "wb") as outfile:
        chart.write_png(outfilepath, scale=scale)


if __name__ == "__main__":
    cli()
