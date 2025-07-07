import pandas as pd
import pytest
from core.reporting import generate_reports


@pytest.fixture
def manifest_path(tmp_path):
    # Build a DataFrame with:
    # - Two entries sharing the same md5_hash ("dup123") → should trigger duplicates.csv
    # - Two entries sharing the same destination_path ("shared/foo.txt") → should trigger name_collisions.md
    df = pd.DataFrame(
        [
            {
                "source_bucket": "b",
                "source_path": "a.txt",
                "file_name": "a.txt",
                "size_bytes": 10,
                "md5_hash": "dup123",
                "action": "MOVE",
                "destination_path": "shared/foo.txt",
            },
            {
                "source_bucket": "b",
                "source_path": "b.txt",
                "file_name": "b.txt",
                "size_bytes": 20,
                "md5_hash": "dup123",
                "action": "MOVE",
                "destination_path": "shared/bar.txt",
            },
            {
                "source_bucket": "b",
                "source_path": "c.txt",
                "file_name": "c.txt",
                "size_bytes": 30,
                "md5_hash": "xyz789",
                "action": "MOVE",
                "destination_path": "shared/foo.txt",
            },
            {
                "source_bucket": "b",
                "source_path": "d.txt",
                "file_name": "d.txt",
                "size_bytes": 40,
                "md5_hash": "unique",
                "action": "MOVE",
                "destination_path": "shared/baz.txt",
            },
        ]
    )
    path = tmp_path / "manifest.parquet"
    df.to_parquet(path)
    return path


def test_generate_reports_creates_duplicates_and_collisions(tmp_path, manifest_path):
    report_dir = tmp_path / "reports"
    report_dir.mkdir()
    report_path = report_dir.as_posix()

    # Run reporting
    generate_reports(str(manifest_path), report_path)

    # Check duplicates.csv
    dup_file = report_dir / "duplicates.csv"
    assert dup_file.exists(), "duplicates.csv should be created"
    dup_df = pd.read_csv(dup_file)
    # Should include exactly the two rows with md5_hash "dup123"
    assert set(dup_df["md5_hash"]) == {"dup123"}
    assert len(dup_df) == 2

    # Check name_collisions.md
    coll_file = report_dir / "name_collisions.md"
    assert coll_file.exists(), "name_collisions.md should be created"
    content = coll_file.read_text()
    # It should mention our collision path
    assert "## Collision at `shared/foo.txt`" in content
    # It should list both source paths a.txt and c.txt
    assert "`a.txt`" in content and "`c.txt`" in content


def test_generate_reports_no_duplicates_or_collisions(tmp_path):
    # Create a manifest with all unique hashes and destinations
    df = pd.DataFrame(
        [
            {
                "source_bucket": "b",
                "source_path": "a.txt",
                "file_name": "a.txt",
                "size_bytes": 10,
                "md5_hash": "h1",
                "action": "MOVE",
                "destination_path": "shared/a.txt",
            },
            {
                "source_bucket": "b",
                "source_path": "b.txt",
                "file_name": "b.txt",
                "size_bytes": 20,
                "md5_hash": "h2",
                "action": "MOVE",
                "destination_path": "shared/b.txt",
            },
        ]
    )
    manifest = tmp_path / "manifest2.parquet"
    df.to_parquet(manifest)

    report_dir = tmp_path / "reports2"
    report_dir.mkdir()
    report_path = report_dir.as_posix()

    # This should run without error and produce no files
    generate_reports(str(manifest), report_path)

    assert not (report_dir / "duplicates.csv").exists()
    assert not (report_dir / "name_collisions.md").exists()
