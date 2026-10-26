import random


def generate(n, seed, dtype):
    if dtype != "float64":
        raise ValueError("unsupported dtype: " + dtype)
    rng = random.Random(seed)
    # Positive dyadic values avoid cancellation and are exactly representable.
    a = [rng.randrange(1, 1025) / 1024.0 for _ in range(n)]
    b = [rng.randrange(1, 1025) / 1024.0 for _ in range(n)]
    return a, b
