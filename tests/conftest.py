import shutil
import subprocess
import time
import pytest
from google.cloud import storage
from types import SimpleNamespace


class FakeBlob(SimpleNamespace):
    def download_as_bytes(self, start=None, end=None):
        return self.content_bytes[start:end]

    def download_as_text(self):
        return self.content_bytes.decode("utf-8")


@pytest.fixture
def blob_factory():
    def _make(name, content=b"", size=0, md5_hash="deadbeef"):
        return FakeBlob(
            name=name,
            bucket=SimpleNamespace(name="bucket"),
            content_bytes=content,
            size=size,
            md5_hash=md5_hash,
        )

    return _make


@pytest.fixture(scope="session", autouse=True)
def fake_gcs_server():
    # Locate the fake-gcs-server binary
    binary = shutil.which("fake-gcs-server")
    if not binary:
        pytest.skip("fake-gcs-server not installed; skipping GCS integration tests")

    # Start it in memory mode on port 4443
    proc = subprocess.Popen(
        [binary, "-scheme", "http", "-port", "4443", "-backend", "memory"],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )
    time.sleep(1)  # give it a moment to bind

    yield  # run all tests

    # Teardown
    proc.terminate()
    proc.wait()


@pytest.fixture
def gcs_client():
    # Point the google storage client at the fake server
    client = storage.Client(
        _http=None,  # ensures it uses requests under the hood
        client_options={"api_endpoint": "http://localhost:4443/storage/v1"},
        project="test-project",
    )
    return client
