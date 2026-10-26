from importlib import import_module

IMPLEMENTATIONS = (
    "cpython-list",
    "cpython-annotated-list",
    "cython-untyped-list",
    "cython-typed-loop-list",
    "cython-native-buffer",
    "numpy-dot",
)


def prepare(name, a, b):
    if name not in IMPLEMENTATIONS:
        raise ValueError("unknown implementation: " + name)
    kernel = import_module(
        "pyramp.benchmarks.dot." + name.replace("-", "_")
    ).dot
    if name == "cython-native-buffer":
        from array import array
        # Memoryview acquisition is also outside the ROI.
        a, b = memoryview(array("d", a)), memoryview(array("d", b))
    elif name == "numpy-dot":
        import numpy as np
        a, b = np.array(a, dtype=np.float64), np.array(b, dtype=np.float64)
    return kernel, a, b
