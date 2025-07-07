"""End-to-end tests against a local fake-gcs-server instance.

These tests spin up the fake-gcs-server in *memory* mode, configure the
Google Cloud SDK / google-cloud-storage client to talk to it (via the
`STORAGE_EMULATOR_HOST` env var), and then run the full FLACCID flow:

1.  Create a bucket and upload a couple of sample blobs
2.  Call `classification.generate_action_plan` → Parquet manifest
3.  Execute the moves with `execution.execute_plan`
4.  Verify with `verify.verify_execution`

No real GCP resources are used.
"""

from __future__ import annotations

import os
import time
import subprocess
from pathlib import Path
import uuid

import pytest
from google.cloud import storage
from google.api_core import exceptions

from core import classification, execution, verify
from shared.utils import GCS_TARGET_DIRS, setup_gcs_client

FAKE_GCS_PORT = 4443  # arbitrary local port
FAKE_GCS_HOST = f"http://localhost:{FAKE_GCS_PORT}"


@pytest.fixture(scope="session", autouse=True)
def _start_fake_gcs():
    """Start fake-gcs-server via Docker for the test session."""
    proc = subprocess.Popen(
        [
            "docker",
            "run",
            "--rm",
            "-p",
            f"{FAKE_GCS_PORT}:4443",
            "fsouza/fake-gcs-server:latest",
            "-scheme",
            "http",
            "-port",
            "4443",
        ],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    # Wait a short moment for the server to be ready
    time.sleep(3)

    # Expose to google-cloud-storage
    os.environ["STORAGE_EMULATOR_HOST"] = FAKE_GCS_HOST

    yield

    proc.terminate()
    proc.wait(timeout=5)


@pytest.fixture()
def gcs_client():
    # `setup_gcs_client` picks up STORAGE_EMULATOR_HOST automatically
    return setup_gcs_client(project_id="test-project")


def test_end_to_end_pipeline(tmp_path: Path, gcs_client: storage.Client, capsys):
    bucket_name = f"test-bucket-{uuid.uuid4().hex[:8]}"
    bucket = gcs_client.bucket(bucket_name)
    try:
        bucket = gcs_client.create_bucket(bucket)
    except exceptions.Conflict:
        bucket = gcs_client.get_bucket(bucket_name)

    # 1. Seed test data
    blob_txt = bucket.blob("source/test.txt")
    blob_txt.upload_from_string("just some text")

    blob_csv = bucket.blob("source/data.csv")
    blob_csv.upload_from_string("id,value\n1,foo\n")

    # 2. Analyze
    # For fake-gcs we build a local tmp Parquet file then upload
    local_manifest = tmp_path / "plan.parquet"

    classification.generate_action_plan(
        client=gcs_client,
        bucket_name=bucket_name,
        prefix="source/",
        manifest_path=str(local_manifest),  # local write
    )
    # NEW: push manifest into fake-gcs
    dest_blob = bucket.blob("plan.parquet")
    dest_blob.upload_from_filename(local_manifest)
    print(f"Manifest file exists after upload: {dest_blob.exists()}")

    manifest_gcs_uri = f"gs://{bucket_name}/plan.parquet"

    # NEW: Print the manifest path for debugging
    print("Manifest written to →", manifest_gcs_uri)

    # Use manifest_gcs_uri in execute_plan and verify_execution
    execution.execute_plan(
        client=gcs_client,
        manifest_path=manifest_gcs_uri,
        max_workers=4,
    )

    verify.verify_execution(
        client=gcs_client,
        manifest_path=manifest_gcs_uri,
    )

    # Assert that the manifest file exists in the bucket
    assert bucket.blob("plan.parquet").exists(), "Manifest file not found in bucket."

    # Assert that files landed in expected prefixes
    assert bucket.blob(
        f"{GCS_TARGET_DIRS['DEFAULT']}test.txt"
    ).exists(), "test.txt not found in DEFAULT prefix."
    assert bucket.blob(
        f"{GCS_TARGET_DIRS['DEFAULT']}data.csv"
    ).exists(), "data.csv not found in DEFAULT prefix."

    # Removed unused variable and updated capture logic
    combined = capsys.readouterr().out

    assert "Moved source/test.txt" in combined
    assert "Moved source/data.csv" in combined
    assert "Verification Summary: 2 OK, 0 FAILED" in combined
