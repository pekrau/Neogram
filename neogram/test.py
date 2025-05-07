"Tests."

import lookup
from piechart import *
from timelines import *
from gantt import *


def test_piechart():
    pyramid = Piechart(style=dict(start=132, label=dict(contrast=True)))
    pyramid += Slice(7, "Shady side")
    pyramid += Slice(18, "Sunny side")
    pyramid += Slice(70, "Sky")

    svg = repr(pyramid.svg())
    pyramid.save("pyramid.yaml")
    pyramid.render("pyramid.svg")

    pyramid2 = lookup.retrieve("pyramid.yaml")
    assert pyramid == pyramid2
    assert svg == repr(pyramid2.svg())


def test_timelines():
    universe = Timelines(title="Universum",
                         style=dict(axis=dict(stroke="lightgrey", absolute=True),
                                    legend=dict(width=False),
                                    padding=4))
    universe += Event(
        "Big Bang",
        -13787000000,
        timeline="Universum",
        style=dict(fill="black", label=dict(anchor="start")),
    )
    universe += Period("Vintergatan", -8800000000, 0, timeline="Universum")
    universe += Period("Jorden", -4567000000, 0)

    universe.save("universe.yaml")
    universe.render("universe.svg")

    universe2 = lookup.retrieve("universe.yaml")
    assert universe == universe2


def test_gantt():
    project = Gantt(style=dict(label=dict(contrast=True), padding=4))
    project += Task("startup", 0.8, 2.2, style=dict(fill="green"))
    project += Task("work", 2.2, 4.8, style=dict(fill="yellow"))
    project += Task("wrapup", 5, 7, style=dict(fill="blue"))
    project.save("project.yaml")
    project.render("project.svg")


if __name__ == "__main__":
    test_piechart()
    test_timelines()
    test_gantt()
