def dot(a: list[float], b: list[float]) -> float:
    total = 0.0
    for i in range(len(a)):
        total += a[i] * b[i]
    return total
