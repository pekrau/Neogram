"Tests."

import io

from diagrams import *


def test_piechart():
    pyramid = Piechart(
        id="pyramid",
        klass="mypiechart",
        start=Degrees(132),
        style=dict(radius=150),
    )
    pyramid += Slice(7, "Shady side", style=dict(label=dict(size=20)))
    pyramid += Slice(18, "Sunny side")
    pyramid += Slice(70, "Sky", style=dict(fill=(1, 200, 210)))

    svg = repr(pyramid.svg())
    pyramid.write("pyramid.svg")
    pyramid.save("pyramid.yaml")

    buffer = io.StringIO()
    pyramid.save(buffer)
    buffer.seek(0)
    pyramid2 = retrieve(buffer)
    assert pyramid == pyramid2
    pyramid3 = retrieve("pyramid.yaml")
    assert pyramid == pyramid3
    assert svg == repr(pyramid3.svg())


def test_timelines():
    universe = Timelines(
        id="universum", epoch=Epoch.ORDINAL, style=dict(width=800, padding=2)
    )
    universe += Event(
        "Big Bang",
        -13787000000,
        timeline="Universum",
        style=dict(label=dict(anchor="start")),
    )
    universe += Period("Vintergatan", -8800000000, 0, timeline="Universum")
    universe += Period("Jorden", -4567000000, 0)
    universe.save("universe.yaml")
    universe.write("universe.svg")
    universe2 = retrieve("universe.yaml")
    assert universe == universe2


# def test_gantt():
#     project = Gantt(id="project")
#     project += Task("startup", 0.8, 2.2, style=dict(fill="cyan"))
#     project += Task("work", 2.2, 4.8)
#     project += Task("wrapup", 5, 7)
#     project.save("project.yaml")
#     project.write("project.svg")


if __name__ == "__main__":
    test_piechart()
    test_timelines()
    # test_gantt()
