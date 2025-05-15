"Test diagrams."

from icecream import ic

import os

from lib import *


TESTS = {
    "timelines": ["universe", "earth", "universe_earth", "poster"],
    "piechart": ["pyramid", "day", "cpies", "rpies"],
    "column": ["universe_earth", "cpies", "cnotes", "notes"],
    "row": ["rpies"],
    "note": ["declaration", "cnotes", "notes", "cpies", "poster"],
    "board": ["poster", "notes"],
}


def get_universe(legend=True):
    universe = Timelines(
        {"text": "Universe", "bold": True, "color": "blue"},
        legend=legend,
        axis={"absolute": True, "caption": "Billion years ago"},
    )
    universe += Event("Big Bang", -13_787_000_000, timeline="Universe", color="red")
    universe += Period(
        "Milky Way galaxy",
        {"value": -7_500_000_000, "low": -8_500_000_000},
        0,
        timeline="Universe",
        color="navy",
        fuzzy="gradient",
    )
    universe += Period("Earth", -4_567_000_000, 0, color="lightgreen")
    universe += Event(
        "Here",
        {"value": -12_000_000_000, "error": 600_000_000},
        timeline="markers",
        marker="none",
        placement="right",
    )
    universe += Event(
        "Circle",
        -10_000_000_000,
        timeline="markers",
        marker="circle",
        color="cyan",
        placement="center",
    )
    universe += Event(
        "Ellipse",
        -8_000_000_000,
        timeline="markers",
        marker="ellipse",
        color="blue",
        placement="left",
    )
    universe += Event(
        "",
        {"value": -6_000_000_000, "low": -6_500_000_000, "high": -5_000_000_000},
        timeline="markers",
        marker="square",
        color="orange",
    )
    universe += Event(
        "Pyramid",
        -4_000_000_000,
        timeline="markers",
        marker="pyramid",
        color="gold",
        placement="center",
    )
    universe += Event(
        "Triangle",
        -2_000_000_000,
        timeline="markers",
        marker="triangle",
        color="purple",
    )
    return universe


def get_earth(legend=True):
    earth = Timelines(
        "Earth", legend=legend, axis={"absolute": True, "caption": "Billion years ago"}
    )
    earth += Period("Earth", -4_567_000_000, 0)
    earth += Period(
        "Archean",
        {"value": -4_000_000_000, "low": -4_100_000_000, "high": -3_950_000_000},
        {"value": -2_500_000_000, "error": 200_000_000},
        color="wheat",
        fuzzy="gradient",
    )
    earth += Event("LUCA?", -4_200_000_000, timeline="Unicellular")
    earth += Period(
        "Unicellular organisms",
        {"value": -3_480_000_000, "low": -4_200_000_000},
        0,
        timeline="Unicellular",
        fuzzy="gradient",
    )
    earth += Period("Eukaryotes", -1_650_000_000, 0)
    earth += Period(
        "Engineers",
        {"value": -3_300_000_000, "error": 200_000_000},
        -1_650_000_000,
        color="lightgray",
        fuzzy="wedge",
    )
    earth += Period("Photosynthesis", -3_400_000_000, 0, color="springgreen")
    earth += Period(
        "Plants",
        -470_000_000,
        0,
        timeline="Photosynthesis",
        color="green",
        placement="left",
    )
    return earth


def test_universe():
    universe = get_universe()
    universe.save("universe.yaml")
    universe.render("universe.svg")

    universe2 = retrieve("universe.yaml")
    assert universe == universe2
    # XXX id's are not equal, since new unique ones are created for each build.
    # assert universe.render() == universe2.render()


def test_earth():
    earth = get_earth()
    earth.save("earth.yaml")
    earth.render("earth.svg")


def test_universe_earth():
    both = Column("Universe and Earth")
    both += get_universe(legend=False)
    both += get_earth(legend=False)
    both.save("universe_earth.yaml")
    both.render("universe_earth.svg")


def test_pyramid():
    pyramid = Piechart("Pyramid", start=132, palette=["#4c78a8", "#9ecae9", "#f58518"])
    pyramid += Slice("Shadow", 7)
    pyramid += Slice("Sunny", 18)
    pyramid += Slice("Sky", 70)
    pyramid.save("pyramid.yaml")
    pyramid.render("pyramid.svg")

    pyramid2 = retrieve("pyramid.yaml")
    assert pyramid == pyramid2
    assert pyramid.render() == pyramid2.render()


def test_day():
    day = Piechart({"text": "Day", "size": 30}, total=24, diameter=400)
    day += Slice("Sleep", 8, color="gray")
    day += Slice("Breakfast", 1, color="lightgreen")
    day += Slice("Gym", 2, color="lightblue")
    day += Slice("Read", 1, color="navy")
    day += Slice("Lunch", 1, color="lightgreen")
    day += Slice("Shuteye", 0.4, color="gray")
    day += Slice("Write", 4.6, color="pink")
    day += Slice("Dinner", 1, color="lightgreen")
    day += Slice("TV", 3, color="orange")
    day += Slice("Read", 2, color="navy")

    day.save("day.yaml")
    day.render("day.svg")

    day2 = retrieve("day.yaml")
    assert day == day2
    assert day.render() == day2.render()


def test_cpies():
    pajer = Column("Pies in column")

    pajer += (paj := Piechart("Strawberry pie", diameter=100))
    paj += Slice("Flour", 7, color="white")
    paj += Slice("Eggs", 2, color="yellow")
    paj += Slice("Butter", 3, color="gold")
    paj += Slice("Strawberries", 3, color="orangered")

    pajer += (paj := Piechart("Rhubarb pie"))
    paj += Slice("Flour", 7, color="white")
    paj += Slice("Eggs", 2, color="yellow")
    paj += Slice("Butter", 3, color="gold")
    paj += Slice("Rhubarb", 3, color="green")

    pajer += Note(
        header="Comment",
        body="Strawberry pie is good.",
        footer={"text": "Copyright 2025 Per Kraulis", "italic": True},
    )

    pajer.save("cpies.yaml")
    pajer.render("cpies.svg")

    pajer2 = retrieve("cpies.yaml")
    assert pajer == pajer2
    assert pajer.render() == pajer2.render()


def test_rpies():
    pajer = Row("Pies in row")

    palette = ["white", "yellow", "gold", "red"]
    pajer += (paj := Piechart("Strawberry pie", diameter=300, palette=palette))
    paj += Slice("Flour", 7)
    paj += Slice("Eggs", 2)
    paj += Slice("Butter", 3)
    paj += Slice("Strawberries", 3)

    pajer += (paj := Piechart("Rhubarb pie", palette=palette))
    paj += Slice("Flour", 7)
    paj += Slice("Eggs", 2)
    paj += Slice("Butter", 3)
    paj += Slice("Rhubarb", 3, color="green")

    pajer.save("rpies.yaml")
    pajer.render("rpies.svg")

    pajer2 = retrieve("rpies.yaml")
    assert pajer == pajer2
    assert pajer.render() == pajer2.render()


def test_declaration():
    decl = Note(
        header={"text": "Declaration", "placement": "left", "bold": True},
        body={"text": "This software was\nwritten by me.", "placement": "right"},
        footer={"text": "Copyright 2025 Per Kraulis", "italic": True},
    )

    decl.save("declaration.yaml")
    decl.render("declaration.svg")


def test_notes():
    column = Column()
    column += Note("Header", "Body", "Footer")
    column += Note("Header", "Body")
    column += Note(body="Body", footer="Footer")
    column += Note("Header")
    column += Note(body="Body")
    column += Note(footer="Footer")
    column += Note("Header", "Body", "Footer", line=0)
    column += {"note": "declaration.yaml"}

    column.save("cnotes.yaml")
    column.render("cnotes.svg")

    board = Board()
    board.append(x=0, y=0, scale=1.5, column=column)
    board.save("notes.yaml")
    board.render("notes.svg")


def test_poster():
    poster = Board("Poster")
    poster.append(
        x=250,
        y=10,
        note=Note("By Per Kraulis", body="Ph.D.", footer="Stockholm University"),
    )
    poster.append(dict(x=0, y=100, timelines=get_universe()))
    poster.append(dict(x=50, y=230, timelines=get_earth()))
    poster.render("poster.svg")
    poster.save("poster.yaml")


def run_tests():
    origdir = os.getcwd()
    try:
        os.chdir("../docs")
        test_universe()
        test_earth()
        test_universe_earth()
        test_pyramid()
        test_day()
        test_cpies()
        test_rpies()
        test_declaration()
        test_notes()
        test_poster()
    finally:
        os.chdir(origdir)


if __name__ == "__main__":
    run_tests()
