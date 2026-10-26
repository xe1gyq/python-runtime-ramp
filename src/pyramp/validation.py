import math


def verify(actual, expected):
    if not math.isfinite(actual) or not math.isclose(
        actual, expected, rel_tol=1e-10, abs_tol=1e-12
    ):
        raise ValueError(f"preflight correctness failure: {actual!r} != {expected!r}")
