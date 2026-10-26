import pytest
from pyramp import data, registry, validation
from pyramp.benchmarks.dot import reference

@pytest.mark.parametrize("name", registry.IMPLEMENTATIONS)
@pytest.mark.parametrize("n,seed", [(1, 0), (17, 42), (257, -3)])
def test_equivalence(name, n, seed):
    a, b = data.generate(n, seed, "float64")
    kernel, x, y = registry.prepare(name, a, b)
    validation.verify(kernel(x, y), reference.dot(a, b))

def test_deterministic():
    assert data.generate(17, 42, "float64") == data.generate(17, 42, "float64")

def test_reject_incorrect():
    with pytest.raises(ValueError):
        validation.verify(2.0, 1.0)
