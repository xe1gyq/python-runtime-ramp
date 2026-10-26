import pytest
from pyramp import cli

@pytest.fixture
def args():
    return cli.parser().parse_args([
        "--benchmark", "dot", "--impl", "cpython-list", "--n", "17",
        "--iterations", "4", "--warmup", "2", "--seed", "42", "--dtype", "float64"])
