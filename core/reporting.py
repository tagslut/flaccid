import pandas as pd


def generate_reports(manifest_path: str, report_path: str):
    print(f"Loading manifest from {manifest_path} to generate reports.")
    try:
        # Adjusted to handle local file paths without storage_options
        df = pd.read_parquet(manifest_path)
    except Exception as e:
        print(f"FATAL: Could not read manifest file. Error: {e}")
        return

    # Duplicates
    duplicates = df[df.duplicated(subset=["md5_hash"], keep=False)].sort_values(
        "md5_hash"
    )
    if not duplicates.empty:
        duplicates_path = f"{report_path.rstrip('/')}/duplicates.csv"
        print(f"Writing duplicates report to: {duplicates_path}")
        duplicates.to_csv(duplicates_path, index=False)
    else:
        print("No duplicates found.")

    # Name collisions
    collisions = df[df.duplicated(subset=["destination_path"], keep=False)].sort_values(
        "destination_path"
    )
    if not collisions.empty:
        collision_path = f"{report_path.rstrip('/')}/name_collisions.md"
        print(f"Writing collision report to: {collision_path}")
        report = "# Name Collision Report\n\n"
        for dest_path, group in collisions.groupby("destination_path"):
            report += f"## Collision at `{dest_path}`\n\n"
            report += "| Source Path | Size | MD5 |\n|---|---|---|\n"
            for _, row in group.iterrows():
                report += f"| `{row['source_path']}` | {row['size_bytes']} | `{row['md5_hash']}` |\n"
            report += "\n"
        with open(collision_path, "w") as f:
            f.write(report)
    else:
        print("No name collisions detected.")
