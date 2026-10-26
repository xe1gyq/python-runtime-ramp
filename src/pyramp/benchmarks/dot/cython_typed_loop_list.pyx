def dot(list a, list b):
    cdef Py_ssize_t i, n = len(a)
    cdef double total = 0.0
    for i in range(n):
        # Both indexed operands are Python objects; multiplication is Python.
        # Its result is converted to double for the native accumulation.
        total += a[i] * b[i]
    return total
