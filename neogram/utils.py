"Neogram: Various utility functions."


import math


def get_ticks(first, last, target=10):
    "Return the tick mark positions for the interval [first, last]."
    step = round((last - first) / target)
    base = 10 ** round(math.log10(step))
    for step in [base, 2*base, 5*base, 10*base]:
        if target * step > (last - first):
            break
    for pos in range(first - step, last + step, step):
        if pos < first:
            continue
        elif pos > last:
            continue
        yield pos
