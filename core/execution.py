import pandas as pd
from google.cloud import storage
from concurrent.futures import ThreadPoolExecutor, as_completed
import tempfile
from urllib.parse import urlparse
from typing import Any


def _execute_single_action(client: Any, action_details: dict) -> str:
    source_bucket_name = action_details["source_bucket"]
    source_path = action_details["source_path"]
    destination_path = action_details["destination_path"]
    action = action_details["action"]

    if action != "MOVE":
        return f"SKIPPED: Action for {source_path} is '{action}', not 'MOVE'."

    try:
        source_bucket = client.bucket(source_bucket_name)
        source_blob = source_bucket.blob(source_path)

        if not source_blob.exists():
            return f"ERROR: Source blob {source_path} not found."

        destination_blob = source_bucket.blob(destination_path)
        rewrite_token = None
        while True:
            rewrite_token, _, _ = destination_blob.rewrite(
                source_blob, token=rewrite_token
            )
            if rewrite_token is None:
                break

        destination_blob.reload()
        new_hash = destination_blob.md5_hash
        expected_hash = source_blob.md5_hash
        if new_hash and expected_hash and new_hash != expected_hash:
            print(
                f"[WARNING] MD5 mismatch for {source_path} after copy. "
                f"Expected {expected_hash}, got {new_hash}. Proceeding anyway."
            )

        source_blob.delete()
        return f"SUCCESS: Moved {source_path} to {destination_path}."
    except Exception as e:
        return f"FAILURE: Error processing {source_path}: {e}"


def _load_manifest(client, manifest_path):
    if manifest_path.startswith("gs://"):
        u = urlparse(manifest_path)
        bucket_name, blob_name = u.netloc, u.path.lstrip("/")
        blob = client.bucket(bucket_name).blob(blob_name)
        # download to a temp file
        tf = tempfile.NamedTemporaryFile(delete=False, suffix=".parquet")
        blob.download_to_filename(tf.name)
        tf.close()
        return pd.read_parquet(tf.name, engine="pyarrow")
    else:
        return pd.read_parquet(manifest_path, engine="pyarrow")


def execute_plan(client: storage.Client, manifest_path: str, max_workers: int):
    print(f"Loading execution plan from {manifest_path}...")
    try:
        df = _load_manifest(client, manifest_path)
    except Exception as e:
        print(f"FATAL: Could not read manifest file. Error: {e}")
        return

    actions_to_run = df[df["action"] == "MOVE"].to_dict("records")
    total_actions = len(actions_to_run)

    if total_actions == 0:
        print("No 'MOVE' actions found. Nothing to execute.")
        return

    print(
        f"Found {total_actions} file operations to execute with {max_workers} workers."
    )
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        future_to_action = {
            executor.submit(_execute_single_action, client, action): action
            for action in actions_to_run
        }
        for i, future in enumerate(as_completed(future_to_action)):
            future_to_action[future]
            try:
                result = future.result()
                print(f"[{i+1}/{total_actions}] {result}")
            except Exception as exc:
                print(f"[{i+1}/{total_actions}] ERROR: {exc}")
