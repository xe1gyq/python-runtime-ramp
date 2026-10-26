# infer_types=False in setup.py: arithmetic locals remain Python objects.
def dot(a, b):
    total = 0.0
    for i in range(len(a)):
        total += a[i] * b[i]
    return total
