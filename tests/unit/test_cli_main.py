from flaccid.cli import main


def test_cli_main_exit_zero(monkeypatch):
    called = {}

    def dummy_app() -> None:
        called["ran"] = True

    monkeypatch.setattr("flaccid.cli.app", dummy_app)

    assert main() == 0
    assert called.get("ran") is True
