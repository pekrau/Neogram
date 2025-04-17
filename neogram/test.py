"Test Neogram."

from icecream import ic

import io

from diagram import *
from piechart import *
from gantt import *


def test_gantt():
    project = Gantt(id="project", date_based=False, style=Style(padding=4))
    project += Task("startup", 100, 200)
    project += Task("work", 200, 600)
    project += Task("wrapup", 600, 700,
                    style=Style(fill="purple", text=dict(italic=True)))
    project.write("project.svg")
    project.write_png("project.png", scale=2.0)


def test_piechart():
    pyramid = Piechart(
        id="pyramid",
        klass="piechart",
        start=Degrees(132),
        style=Style(palette=Palette("#4c78a8", "#9ecae9", "#f58518")),
    )
    pyramid += Slice(7, "Shady side")
    pyramid += (18, "Sunny side")
    pyramid += Slice(70, "Sky")
    pyramid.write("pyramid.svg")
    pyramid.write_png("pyramid.png", scale=2.0)
    contents1 = pyramid.as_dict()
    buffer = io.StringIO()
    pyramid.save(buffer)
    buffer.seek(0)
    pyramid.save("pyramid.yaml")
    pyramid2 = retrieve(buffer)
    assert pyramid == pyramid2
    pyramid3 = retrieve("pyramid.yaml")
    assert pyramid == pyramid3


if __name__ == "__main__":
    test_piechart()
    test_gantt()
