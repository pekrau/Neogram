"Convert Neogram YAML file to PNG."

import io
import pathlib

import cairosvg
import click

from diagrams import retrieve


def validate_scale(ctx, param, value):
    if value <= 0.0:
        raise click.BadParameter("scale must be larger than 0.0")
    return value


@click.command()
@click.option("-s", "--scale", default=1.0, type=float, callback=validate_scale)
@click.argument("infilepath", nargs=1, required=True)
@click.argument("outfilepath", nargs=1, required=False)
def topng(scale, infilepath, outfilepath):
    infilepath = pathlib.Path(infilepath)
    if not infilepath.exists():
        raise click.BadParameter("no such input file")
    diagram = retrieve(infilepath)
    if not outfilepath:
        outfilepath = infilepath.with_suffix(".png")
    with open(outfilepath, "wb") as outfile:
        inputfile = io.StringIO(repr(diagram.svg_document()))
        outfile.write(cairosvg.svg2png(file_obj=inputfile, scale=scale))


if __name__ == "__main__":
    topng()
