import pytest
from pyramp import cli, registry

@pytest.mark.parametrize("flag,value", [
    ("--impl", "unknown"), ("--n", "0"), ("--n", "-1"),
    ("--iterations", "0"), ("--iterations", "-1"),
    ("--warmup", "-1"), ("--dtype", "float32")])
def test_invalid(args, flag, value):
    argv = ["--benchmark", "dot", "--impl", args.impl, "--n", str(args.n),
            "--iterations", "4", "--warmup", "2", "--seed", "42", "--dtype", "float64"]
    argv[argv.index(flag)+1] = value
    with pytest.raises(SystemExit) as exc:
        cli.main(argv)
    assert exc.value.code == 2

@pytest.mark.parametrize("name", registry.IMPLEMENTATIONS)
def test_same_cli(name):
    assert cli.main(["--benchmark", "dot", "--impl", name, "--n", "8",
                     "--iterations", "2", "--warmup", "0", "--seed", "42",
                     "--dtype", "float64"]) == 0
