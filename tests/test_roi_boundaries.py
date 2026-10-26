import pytest
from pyramp import cli

def instrument(monkeypatch):
    events = []
    active = False
    def outside(name, fn):
        def wrapped(*args):
            assert not active, name + " inside ROI"
            events.append(name)
            return fn(*args)
        return wrapped
    monkeypatch.setattr(cli.data, "generate", outside("generate", cli.data.generate))
    monkeypatch.setattr(cli.reference, "dot", outside("reference", cli.reference.dot))
    monkeypatch.setattr(cli.validation, "verify", outside("validate", cli.validation.verify))
    original = cli.registry.prepare
    def prepare(*args):
        assert not active
        events.append("prepare")
        kernel, a, b = original(*args)
        def run(x, y):
            events.append("measured" if active else "kernel")
            return kernel(x, y)
        return run, a, b
    def begin():
        nonlocal active
        events.append("begin")
        active = True
    def end():
        nonlocal active
        assert active
        events.append("end")
        active = False
    monkeypatch.setattr(cli.registry, "prepare", prepare)
    monkeypatch.setattr(cli.roi, "begin", begin)
    monkeypatch.setattr(cli.roi, "end", end)
    return events

def test_sequence(monkeypatch, args):
    events = instrument(monkeypatch)
    cli.execute(args)
    assert events == ["generate", "prepare", "reference", "kernel", "validate",
                      "kernel", "kernel", "begin"] + ["measured"] * 4 + ["end"]

def test_failed_preflight_prevents_roi(monkeypatch, args):
    events = instrument(monkeypatch)
    def fail(*args):
        raise ValueError("incorrect")
    monkeypatch.setattr(cli.validation, "verify", fail)
    with pytest.raises(ValueError):
        cli.execute(args)
    assert "begin" not in events
