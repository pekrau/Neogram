"Test Neogram."

from icecream import ic

from common import *


if __name__ == "__main__":
    import io

    pyramid = Piechart(
        id="pyramid",
        klass="piechart",
        start=Degrees(132),
        style=Style(palette=Palette("#4c78a8", "#9ecae9", "#f58518")),
    )
    pyramid += Slice(10, "Shady side")
    pyramid += (15, "Sunny side")
    pyramid += Slice(70, "Sky")
    pyramid.write("pyramid.svg")
    contents1 = pyramid.as_dict()
    buffer = io.StringIO()
    write(pyramid, buffer)
    buffer.seek(0)
    with open("pyramid.yaml", "w") as outfile:
        outfile.write(buffer.read())
    buffer.seek(0)
    pyramid = read(buffer)
    contents2 = pyramid.as_dict()
    assert contents1 == contents2
    pyramid.write_png("pyramid.png")
