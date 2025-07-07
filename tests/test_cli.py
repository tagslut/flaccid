import pytest
from typer.testing import CliRunner
from fla import app  # Updated to point to fla/__main__.py

from types import SimpleNamespace


@pytest.fixture
def runner():
    return CliRunner()


class DummyClient:
    def bucket(self, name):
        return SimpleNamespace(
            list_blobs=lambda prefix: [],
        )


@pytest.fixture(autouse=True)
def patch_gcs(monkeypatch):
    # Patch setup_gcs_client to return our dummy client everywhere
    monkeypatch.setattr("shared.utils.setup_gcs_client", lambda proj: DummyClient())
    # Patch get_gcs_bucket_name to just strip "gs://"
    monkeypatch.setattr(
        "shared.utils.get_gcs_bucket_name",
        lambda uri: uri.replace("gs://", "").strip("/"),
    )
    # Patch classification/reporting/execution/verify to no-ops
    monkeypatch.setattr(
        "core.classification.generate_action_plan",
        lambda *args, **kwargs: print("CLASSIFY OK"),
    )
    monkeypatch.setattr(
        "core.reporting.generate_reports", lambda *args, **kwargs: print("REPORT OK")
    )
    monkeypatch.setattr(
        "core.execution.execute_plan", lambda *args, **kwargs: print("EXECUTE OK")
    )
    monkeypatch.setattr(
        "core.verify.verify_execution", lambda *args, **kwargs: print("VERIFY OK")
    )
    monkeypatch.setattr(
        "fla.verify_execution",
        lambda *args, **kwargs: print("VERIFY OK"),
        raising=False,
    )


def test_analyze_cmd(runner):
    result = runner.invoke(
        app,
        [
            "analyze",
            "--source-uri",
            "gs://bucket/pfx",
            "--project-id",
            "proj",
            "--manifest-path",
            "/tmp/plan.parquet",
        ],
    )
    assert result.exit_code == 0
    assert "CLASSIFY OK" in result.stdout


def test_report_cmd(runner):
    result = runner.invoke(
        app,
        [
            "report",
            "--manifest-path",
            "/tmp/plan.parquet",
            "--report-path",
            "/tmp/reports/",
        ],
    )
    assert result.exit_code == 0
    assert "REPORT OK" in result.stdout


def test_execute_cmd(runner):
    result = runner.invoke(
        app,
        [
            "execute",
            "--manifest-path",
            "/tmp/plan.parquet",
            "--project-id",
            "proj",
            "--workers",
            "8",
        ],
    )
    assert result.exit_code == 0
    assert "EXECUTE OK" in result.stdout


def test_verify_cmd(runner):
    result = runner.invoke(
        app,
        [
            "verify",
            "--manifest-path",
            "/tmp/plan.parquet",
            "--project-id",
            "proj",
        ],
    )
    assert result.exit_code == 0
    assert "VERIFY OK" in result.stdout
