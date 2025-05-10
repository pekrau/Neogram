"Test diagrams."

import icecream

icecream.install()

from lib import *


def test_universum():
    universum = Timelines({"text": "Universum", "bold": True, "color": "red"}, 600)
    universum += Event("Big Bang", -13_787_000_000, timeline="Universum", color="red")
    universum += Period("Vintergatan", -8_000_000_000, 0, timeline="Universum", color="navy")
    universum += Period("Jorden", -4_567_000_000, 0, color="lightgreen")
    universum.save("universum.yaml")
    universum.render("universum.svg")


def test_jorden():
    jorden = Timelines("Jorden", 600)
    jorden += Period("Jorden", -4_567_000_000, 0)
    jorden += Event("LUCA?", -4_200_000_000, timeline="Encelliga")
    jorden += Period("Encelliga organismer", -3_480_000_000, 0, timeline="Encelliga")
    jorden += Period("Eukaryoter", -1_650_000_000, 0)
    jorden += Period("Fotosyntes", -3_400_000_000, 0)
    jorden += Period("Landväxter", -470_000_000, 0, timeline="Fotosyntes")
    jorden.save("jorden.yaml")
    jorden.render("jorden.svg")


def test_pyramid():
    pyramid = Piechart("Pyramid", start=132)
    pyramid += Slice("Skuggsida", 7)
    pyramid += Slice("Solsida", 18)
    pyramid += Slice("Himmel", 70)
    pyramid.save("pyramid.yaml")
    pyramid.render("pyramid.svg")

    pyramid2 = retrieve("pyramid.yaml")
    assert pyramid == pyramid2
    assert pyramid.render() == pyramid2.render()


def test_dagen():
    dagen = Piechart({"text": "Dagen", "size": 30}, total=24)
    dagen += Slice("Sova", 8, color="gray")
    dagen += Slice("Frukost", 1, color="lightgreen")
    dagen += Slice("Träna", 2, color="lightblue")
    dagen += Slice("Läsa", 1, color="navy")
    dagen += Slice("Lunch", 1, color="lightgreen")
    dagen += Slice("Tupplur", 0.4, color="gray")
    dagen += Slice("Skriva", 4.6, color="pink")
    dagen += Slice("Middag", 1, color="lightgreen")
    dagen += Slice("TV", 3, color="orange")
    dagen += Slice("Läsa", 2, color="navy")
    dagen.save("dagen.yaml")
    dagen.render("dagen.svg")


if __name__ == "__main__":
    test_universum()
    test_jorden()
    test_pyramid()
    test_dagen()
