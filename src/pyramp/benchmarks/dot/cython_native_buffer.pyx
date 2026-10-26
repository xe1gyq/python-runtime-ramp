import cython


@cython.boundscheck(False)
@cython.wraparound(False)
def dot(const double[::1] a, const double[::1] b):
    cdef Py_ssize_t i, n = a.shape[0]
    cdef double total = 0.0
    if b.shape[0] != n:
        raise ValueError("input lengths differ")
    for i in range(n):
        total += a[i] * b[i]
    return total
