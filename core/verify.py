import pandas as pd
from google.cloud import storage
import tempfile
from urllib.parse import urlparse


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


def verify_execution(client: storage.Client, manifest_path: str):
    print(f"Loading manifest from {manifest_path} for verification.")
    try:
        df = _load_manifest(client, manifest_path)
    except Exception as e:
        print(f"FATAL: Could not read manifest file at {manifest_path}. Error: {e}")
        return

    actions = df[df["action"] == "MOVE"].to_dict("records")
    total = len(actions)

    if total == 0:
        print("No 'MOVE' actions found. Nothing to verify.")
        return

    success = 0
    failure = 0

    for i, action in enumerate(actions):
        bucket = client.bucket(action["source_bucket"])
        src = bucket.blob(action["source_path"])
        dst = bucket.blob(action["destination_path"])
        src_exists = src.exists()
        dst_exists = dst.exists()

        print(
            f"[{i+1}/{total}] Verifying {action['source_path']} -> {action['destination_path']}...",
            end=" ",
        )
        if not src_exists and dst_exists:
            print("OK")
            success += 1
        else:
            print("FAILED")
            if src_exists:
                print(f" - Source still exists: {action['source_path']}")
            if not dst_exists:
                print(f" - Destination missing: {action['destination_path']}")
            failure += 1

    print(f"\nVerification Summary: {success} OK, {failure} FAILED.")
    if failure == 0:
        print("\nVerification PASSED")
    else:
        print("\nVerification FAILED")
