import importlib

from flaccid.plugins import registry


def test_import_core_does_not_load_plugins(monkeypatch):
    called = False

    def fake_load_plugins() -> None:
        nonlocal called
        called = True

    monkeypatch.setattr(registry, "load_plugins", fake_load_plugins)

    importlib.reload(importlib.import_module("flaccid.core"))

    assert called is False
