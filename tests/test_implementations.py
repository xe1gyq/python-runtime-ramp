import ast
import importlib
import inspect
from pyramp import data, registry
from pyramp.benchmarks.dot import cpython_list, cpython_annotated_list

def test_negative_control():
    trees = []
    for module in (cpython_list, cpython_annotated_list):
        tree = ast.parse(inspect.getsource(module.dot))
        fn = tree.body[0]
        fn.returns = None
        for arg in fn.args.args:
            arg.annotation = None
        trees.append(ast.dump(tree, include_attributes=False))
    assert trees[0] == trees[1]
    a, b = data.generate(8, 42, "float64")
    for name in registry.IMPLEMENTATIONS[:4]:
        _, x, y = registry.prepare(name, a, b)
        assert x is a and y is b
        assert type(x) is list and all(type(v) is float for v in x)

def test_native_representations():
    a, b = data.generate(8, 42, "float64")
    _, x, y = registry.prepare("cython-native-buffer", a, b)
    assert x.contiguous and x.format == "d" and x.itemsize == 8
    assert list(x) == a and list(y) == b
    _, x, y = registry.prepare("numpy-dot", a, b)
    assert x.dtype.name == "float64" and x.flags.c_contiguous
    assert x.tolist() == a and y.tolist() == b

def test_compiled_extensions_importable():
    for name in registry.IMPLEMENTATIONS[2:5]:
        module = importlib.import_module("pyramp.benchmarks.dot." + name.replace("-", "_"))
        assert module.__file__.endswith(".so")
