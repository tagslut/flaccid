import pytest
from types import SimpleNamespace
from core.execution import _execute_single_action


class DummyBlob(SimpleNamespace):
    def __init__(self, name, md5_hash, exists=True):
        super().__init__(name=name, md5_hash=md5_hash)
        self._exists = exists
        self.delete_called = False
        # simulate destination blob state
        self._rewrite_calls = 0

    def exists(self):
        return self._exists

    def reload(self):
        # no-op for metadata reload
        pass

    def delete(self):
        self.delete_called = True

    def rewrite(self, source_blob, token=None):
        # on first call return a token, on second, finish
        self._rewrite_calls += 1
        if self._rewrite_calls == 1:
            return ("token1", None, None)
        return (None, None, None)


class DummyBucket:
    def __init__(self, blobs):
        # blobs: dict[str, DummyBlob]
        self._blobs = blobs

    def blob(self, path):
        if path not in self._blobs:
            # simulate non-existent
            b = DummyBlob(name=path, md5_hash="", exists=False)
            self._blobs[path] = b
        return self._blobs[path]


class DummyClient:
    def __init__(self, bucket_name, blobs):
        self._bucket = DummyBucket(blobs)

    def bucket(self, bucket_name):
        return self._bucket


@pytest.fixture
def fake_client_and_blobs(tmp_path):
    # Setup a source and dest blob with matching MD5
    src = DummyBlob(name="src.txt", md5_hash="abc123", exists=True)
    dest = DummyBlob(name="archive/src.txt", md5_hash="abc123", exists=True)
    blobs = {
        "src.txt": src,
        "archive/src.txt": dest,
    }
    client = DummyClient("dummy-bucket", blobs)
    return client, blobs


def test_execute_success(fake_client_and_blobs):
    client, blobs = fake_client_and_blobs
    action = {
        "source_bucket": "dummy-bucket",
        "source_path": "src.txt",
        "destination_path": "archive/src.txt",
        "action": "MOVE",
    }
    result = _execute_single_action(client, action)
    assert result.startswith("SUCCESS"), "Should report success"
    # ensure delete was called on source blob
    assert blobs["src.txt"].delete_called


def test_execute_skip_non_move(fake_client_and_blobs):
    client, blobs = fake_client_and_blobs
    action = {
        "source_bucket": "dummy-bucket",
        "source_path": "src.txt",
        "destination_path": "archive/src.txt",
        "action": "COPY",  # not MOVE
    }
    result = _execute_single_action(client, action)
    assert "SKIPPED" in result


def test_execute_error_missing_source():
    # Blob that does not exist
    client = DummyClient("dummy-bucket", {})
    action = {
        "source_bucket": "dummy-bucket",
        "source_path": "nope.txt",
        "destination_path": "archive/nope.txt",
        "action": "MOVE",
    }
    result = _execute_single_action(client, action)
    assert "ERROR: Source blob nope.txt not found." in result


def test_execute_md5_mismatch(fake_client_and_blobs, capsys):
    client, blobs = fake_client_and_blobs
    # set dest blob md5 different
    blobs["archive/src.txt"].md5_hash = "wrong"
    action = {
        "source_bucket": "dummy-bucket",
        "source_path": "src.txt",
        "destination_path": "archive/src.txt",
        "action": "MOVE",
    }
    # Updated test to capture stdout and assert warning
    result = _execute_single_action(client, action)
    captured = capsys.readouterr()
    assert "[WARNING] MD5 mismatch" in captured.out
    assert "SUCCESS: Moved" in result
