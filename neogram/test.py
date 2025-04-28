"Tests."

import lookup
from piechart import *
from timelines import *
from gantt import *


def test_piechart():
    pyramid = Piechart(
        id="pyramid",
        start=Degrees(132),
        style=dict(radius=150),
    )
    pyramid += Slice(7, "Shady side", style=dict(label=dict(size=20)))
    pyramid += Slice(18, "Sunny side")
    pyramid += Slice(70, "Sky", style=dict(fill=(1, 200, 210)))

    svg = repr(pyramid.svg())
    pyramid.save("pyramid.yaml")
    pyramid.render("pyramid.svg")

    pyramid2 = lookup.retrieve("pyramid.yaml")
    assert pyramid == pyramid2
    assert svg == repr(pyramid2.svg())


def test_timelines():
    universe = Timelines(
        id="universum", epoch=Epoch.ORDINAL, style=dict(padding=2, legend=dict(bold=True))
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
    universe.render("universe.svg")
    universe2 = lookup.retrieve("universe.yaml")
    assert universe == universe2


def test_gantt():
    project = Gantt(id="project", style=dict(padding=2))
    project += Task("startup", 0.8, 2.2, style=dict(fill="cyan"))
    project += Task("work", 2.2, 4.8)
    project += Task("wrapup", 5, 7)
    project.save("project.yaml")
    project.render("project.svg")


if __name__ == "__main__":
    test_piechart()
    test_timelines()
    test_gantt()
