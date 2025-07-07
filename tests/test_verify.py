import pandas as pd
import pytest
from types import SimpleNamespace
from core import verify


class DummyBlob(SimpleNamespace):
    def __init__(self, exists):
        super().__init__()
        self._exists = exists

    def exists(self):
        return self._exists


class DummyBucket:
    def __init__(self, blobs):
        # blobs: mapping path -> DummyBlob
        self._blobs = blobs

    def blob(self, path):
        # return a blob object, defaulting to exists=False if unknown
        return self._blobs.get(path, DummyBlob(False))


class DummyClient:
    def __init__(self, bucket_name, blobs):
        self._bucket_name = bucket_name
        self._bucket = DummyBucket(blobs)

    def bucket(self, name):
        assert name == self._bucket_name
        return self._bucket


@pytest.fixture
def manifest_file(tmp_path):
    # Create a manifest DataFrame with two MOVE actions
    df = pd.DataFrame(
        [
            {
                "source_bucket": "b",
                "source_path": "foo.txt",
                "file_name": "foo.txt",
                "size_bytes": 123,
                "md5_hash": "h1",
                "action": "MOVE",
                "destination_path": "dest/foo.txt",
            },
            {
                "source_bucket": "b",
                "source_path": "bar.txt",
                "file_name": "bar.txt",
                "size_bytes": 456,
                "md5_hash": "h2",
                "action": "MOVE",
                "destination_path": "dest/bar.txt",
            },
        ]
    )
    path = tmp_path / "manifest.parquet"
    df.to_parquet(path)
    return str(path)


def test_verify_all_ok(capsys, manifest_file):
    # source no longer exists, dest does exist
    blobs = {
        "foo.txt": DummyBlob(False),
        "dest/foo.txt": DummyBlob(True),
        "bar.txt": DummyBlob(False),
        "dest/bar.txt": DummyBlob(True),
    }
    client = DummyClient("b", blobs)

    verify.verify_execution(client, manifest_file)

    out = capsys.readouterr().out
    assert "Verification PASSED" in out


def test_verify_failures(capsys, manifest_file):
    # simulate failures: source still exists, dest missing
    blobs = {
        "foo.txt": DummyBlob(True),  # still there
        "dest/foo.txt": DummyBlob(False),
        "bar.txt": DummyBlob(False),
        "dest/bar.txt": DummyBlob(False),
    }
    client = DummyClient("b", blobs)

    verify.verify_execution(client, manifest_file)

    out = capsys.readouterr().out
    assert "Verification FAILED" in out
    # we don’t care about exact row order / spacing
