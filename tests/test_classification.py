from core.classification import _classify_blob


def test_archive_extension(blob_factory):
    b = blob_factory("foo.bak", content=b"", size=10)
    result = _classify_blob(b.bucket, b)
    assert result["destination_key"] == "ARCHIVE"


def test_discard_confidential(blob_factory):
    b = blob_factory("secret.txt", content=b"This is Confidential data", size=30)
    result = _classify_blob(b.bucket, b)
    assert result["destination_key"] == "DISCARD"


def test_log_with_error(blob_factory):
    b = blob_factory("app.log", content=b"all good\nFATAL error\n", size=20)
    result = _classify_blob(b.bucket, b)
    assert result["destination_key"] == "DISCARD"


def test_invalid_python(blob_factory):
    bad_code = b"def broken(:\n pass"
    b = blob_factory("script.py", content=bad_code, size=len(bad_code))
    result = _classify_blob(b.bucket, b)
    assert result["destination_key"] == "LABS_DUMP"


def test_default_shared(blob_factory):
    b = blob_factory("image.png", content=b"\x89PNG\r\n", size=100)
    result = _classify_blob(b.bucket, b)
    assert result["destination_key"] == "DEFAULT"
