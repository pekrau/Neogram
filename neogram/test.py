"Test diagrams."

from lookup import *


def test_timelines():
    universum = Timelines("Universum")
    universum += Event("Big Bang", -13_787_000_000, timeline="Universum")
    universum += Period("Vintergatan", -8_000_000_000, 0, timeline="Universum")
    universum += Period("Jorden", -4_567_000_000, 0)
    universum.save("universum.yaml")
    universum.render("universum.svg")


if __name__ == "__main__":
    test_timelines()
