import os
import ast
import pandas as pd
from google.cloud import storage
from concurrent.futures import ThreadPoolExecutor, as_completed
from shared.utils import GCS_TARGET_DIRS


def _classify_blob(bucket: storage.Bucket, blob: storage.Blob) -> dict:
    file_name = os.path.basename(blob.name)
    _, extension = os.path.splitext(file_name)
    extension = extension.lower()
    action = "MOVE"
    destination_key = "DEFAULT"

    # Rule 1: Archival based on extension
    if extension in [".bak", ".tmp", ".old", ".archive"]:
        destination_key = "ARCHIVE"

    # Rule 2: Discard based on content or name for log files
    elif extension == ".log":
        try:
            content_sample = (
                blob.download_as_bytes(start=0, end=4096)
                .decode("utf-8", errors="ignore")
                .upper()
            )
            if "ERROR" in content_sample or "FATAL" in content_sample:
                destination_key = "DISCARD"
        except Exception:
            pass

    # Rule 3: Tagging for CSV
    elif extension == ".csv":
        destination_key = "DEFAULT"

    # Rule 4: Getting for documents
    elif extension in [".pdf", ".docx"]:
        destination_key = "GET"

    # Rule 5: Labs Dump for Python and notebooks
    elif extension == ".py":
        try:
            source_code = blob.download_as_text()
            ast.parse(source_code)
        except (SyntaxError, ValueError, Exception):
            destination_key = "LABS_DUMP"
    elif extension == ".ipynb":
        destination_key = "LABS_DUMP"

    # Rule 6: Discard based on content for any other extension
    else:
        try:
            content_sample = blob.download_as_bytes(start=0, end=4096).decode(
                "utf-8", errors="ignore"
            )
            if "confidential" in content_sample.lower():
                destination_key = "DISCARD"
        except Exception:
            pass

    destination_path = os.path.join(GCS_TARGET_DIRS[destination_key], file_name)
    return {
        "source_bucket": blob.bucket.name,
        "source_path": blob.name,
        "file_name": file_name,
        "size_bytes": blob.size,
        "md5_hash": blob.md5_hash,
        "action": action,
        "destination_key": destination_key,
        "destination_path": destination_path,
    }


def generate_action_plan(
    client: storage.Client, bucket_name: str, prefix: str, manifest_path: str
):
    bucket = client.bucket(bucket_name)
    blobs_to_process = list(client.list_blobs(bucket, prefix=prefix))
    if not blobs_to_process:
        print("No blobs found. Exiting analysis.")
        return

    all_actions = []
    with ThreadPoolExecutor(max_workers=32) as executor:
        future_to_blob = {
            executor.submit(_classify_blob, bucket, blob): blob
            for blob in blobs_to_process
        }
        for i, future in enumerate(as_completed(future_to_blob)):
            blob = future_to_blob[future]
            try:
                result = future.result()
                all_actions.append(result)
                print(
                    f"[{i+1}/{len(blobs_to_process)}] Classified: {blob.name} -> {result['destination_key']}"
                )
            except Exception as exc:
                print(f"Error classifying {blob.name}: {exc}")
                all_actions.append(
                    {
                        "source_bucket": bucket_name,
                        "source_path": blob.name,
                        "file_name": os.path.basename(blob.name),
                        "size_bytes": blob.size,
                        "md5_hash": blob.md5_hash,
                        "action": "ERROR",
                        "destination_key": "ERROR",
                        "destination_path": f"Error: {exc}",
                    }
                )

    df = pd.DataFrame(all_actions)
    if manifest_path.startswith("gs://"):
        df.to_parquet(
            manifest_path,
            engine="pyarrow",
            storage_options={"token": "google_default"},
        )
    else:  # local file
        df.to_parquet(manifest_path, engine="pyarrow")
