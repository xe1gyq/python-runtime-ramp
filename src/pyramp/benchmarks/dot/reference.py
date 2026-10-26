import math


def dot(a, b):
    return math.fsum(x * y for x, y in zip(a, b, strict=True))
