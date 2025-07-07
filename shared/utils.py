from google.cloud import storage
from urllib.parse import urlparse

GCS_TARGET_DIRS = {
    "ARCHIVE": "archive/",
    "DISCARD": "discard/",
    "LABS_DUMP": "labs_dump/",
    "TAG": "tag/",
    "GET": "get/",
    "DEFAULT": "shared/",
    "ERROR": "error/",
}

_GCS_CLIENT = None


def setup_gcs_client(project_id: str) -> storage.Client:
    global _GCS_CLIENT
    if _GCS_CLIENT is None:
        _GCS_CLIENT = storage.Client(project=project_id)
    return _GCS_CLIENT


def get_gcs_bucket_name(uri: str) -> str:
    parsed_uri = urlparse(uri)
    if parsed_uri.scheme != "gs":
        raise ValueError("URI must start with gs://")
    return parsed_uri.netloc
