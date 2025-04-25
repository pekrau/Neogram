"Test Neogram."

from icecream import ic

import io

from diagrams import *


def test_timelines():
    universe = Timelines(id="universum", epoch=Epoch.ORDINAL, width=800)
    universe += Event("Big Bang", -13787000000, timeline="Universum", style=dict(fill="black"))
    universe += Period("Vintergatan", -8800000000, 0, timeline="Universum")
    universe += Period("Jorden", -4567000000, 0, style=dict(fill="green"))
    universe.save("universe.yaml")
    universe.write("universe.svg")


# def test_gantt():
#     project = Gantt(id="project")
#     project += Task("startup", 0.8, 2.2, style=dict(fill="cyan"))
#     project += Task("work", 2.2, 4.8)
#     project += Task("wrapup", 5, 7)
#     project.save("project.yaml")
#     project.write("project.svg")


def test_piechart():
    pyramid = Piechart(
        id="pyramid",
        klass="mypiechart",
        start=Degrees(132),
        style=dict(label=dict(contrast=True)),
    )
    pyramid += Slice(7, "Shady side", style=dict(label=dict(size=20)))
    pyramid += (18, "Sunny side")
    pyramid += Slice(70, "Sky", style=dict(stroke="grey", stroke_width=1))

    svg = repr(pyramid.svg())
    pyramid.write("pyramid.svg")
    pyramid.save("pyramid.yaml")

    contents1 = pyramid.as_dict()
    buffer = io.StringIO()
    pyramid.save(buffer)
    buffer.seek(0)
    pyramid2 = retrieve(buffer)
    assert pyramid == pyramid2
    pyramid3 = retrieve("pyramid.yaml")
    assert pyramid == pyramid3
    assert svg == repr(pyramid3.svg())


if __name__ == "__main__":
    test_piechart()
    # test_gantt()
    test_timelines()
