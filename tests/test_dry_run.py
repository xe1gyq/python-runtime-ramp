from pyramp import cli

def test_no_execution_or_markers(monkeypatch, capsys):
    def forbidden(*args, **kwargs):
        raise AssertionError("dry run executed workload or emitted a marker")
    monkeypatch.setattr(cli, "execute", forbidden)
    monkeypatch.setattr(cli.data, "generate", forbidden)
    monkeypatch.setattr(cli.registry, "prepare", forbidden)
    monkeypatch.setattr(cli.roi, "begin", forbidden)
    monkeypatch.setattr(cli.roi, "end", forbidden)
    assert cli.main(["--benchmark", "dot", "--impl", "cython-native-buffer",
                     "--n", "4096", "--iterations", "100", "--warmup", "3",
                     "--seed", "42", "--dtype", "float64", "--dry-run"]) == 0
    output = capsys.readouterr().out
    assert "Dry run only. No kernel executed." in output
    assert "prepare implementation representation" in output
