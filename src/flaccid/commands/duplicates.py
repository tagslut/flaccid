from __future__ import annotations

import os
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional, Tuple

import typer
from rich.console import Console
from rich.progress import track
from rich.prompt import Confirm, Prompt
from rich.table import Table

from flaccid.utils.audio import (
    extract_flac_metadata,
    format_duration,
    format_size,
    get_audio_quality_score,
    get_file_hash,
)

app = typer.Typer(help="Find and manage duplicate FLAC files in your library.")
console = Console()


# --------------------------------------------------------------------------- #
# Shared helpers                                                              #
# --------------------------------------------------------------------------- #
def _gather_flac_files(folder: Path, recursive: bool = True) -> List[Path]:
    """Return a list of FLAC files located in *folder*."""
    if recursive:
        return [p for p in folder.rglob("*.flac") if p.is_file()]
    return [p for p in folder.glob("*.flac") if p.is_file()]


def _group_files_by(files: Iterable[Path], method: str) -> Dict[str, List[Path]]:
    """
    Group FLAC files according to *method*.

    Supported methods: hash | filename | title | artist+title
    """
    valid = {"hash", "filename", "title", "artist+title"}
    if method not in valid:
        raise ValueError(f"Unsupported method {method!r}")

    groups: Dict[str, List[Path]] = {}

    for file_path in files:
        try:
            if method == "hash":
                key = get_file_hash(file_path)
            elif method == "filename":
                key = file_path.name.lower()
            else:
                meta = extract_flac_metadata(file_path)
                if "error" in meta:
                    continue
                tags = meta.get("tags", {})
                if method == "title":
                    key = tags.get("title", "").lower()
                else:  # artist+title
                    artist = tags.get("artist", "").lower()
                    title = tags.get("title", "").lower()
                    key = f"{artist} - {title}" if artist and title else ""
                if not key:
                    continue
        except Exception as exc:  # noqa: BLE001
            console.print(f"❌ Error analysing {file_path}: {exc}", style="red")
            continue

        groups.setdefault(key, []).append(file_path)

    return groups


def _get_file_creation_time(file_path: Path) -> datetime:
    stat = file_path.stat()
    if hasattr(stat, "st_birthtime"):  # macOS
        return datetime.fromtimestamp(stat.st_birthtime)
    return datetime.fromtimestamp(stat.st_mtime)


def _calculate_duplicate_metrics(
    files: List[Path],
) -> List[Tuple[Path, Dict[str, Any]]]:
    """Return (file, metrics) tuples used by selection strategies."""
    metrics: List[Tuple[Path, Dict[str, Any]]] = []
    for p in files:
        meta = extract_flac_metadata(p)
        metrics.append(
            (
                p,
                {
                    "creation_time": _get_file_creation_time(p),
                    "quality_score": get_audio_quality_score(meta)
                    if "error" not in meta
                    else 0,
                    "size": meta.get("size", 0),
                    "metadata": meta,
                },
            )
        )
    return metrics


def _select_best_file(files: List[Path], strategy: str) -> Optional[Path]:
    """Return the file to keep depending on *strategy*."""
    if len(files) <= 1:
        return files[0] if files else None

    metrics = _calculate_duplicate_metrics(files)

    match strategy:
        case "keep-newest":
            metrics.sort(key=lambda x: x[1]["creation_time"], reverse=True)
        case "keep-oldest":
            metrics.sort(key=lambda x: x[1]["creation_time"])
        case "keep-highest-quality":
            metrics.sort(
                key=lambda x: (x[1]["quality_score"], x[1]["size"]), reverse=True
            )
        case _:
            return None

    return metrics[0][0]


# --------------------------------------------------------------------------- #
# duplicates find                                                             #
# --------------------------------------------------------------------------- #
@app.command("find")
def find_duplicates(
    directory: str = typer.Argument(..., help="Directory to scan"),
    by: str = typer.Option("hash", help="hash | title | filename | artist+title"),
    recursive: bool = typer.Option(True, help="Recurse into sub-folders"),
    min_size: int = typer.Option(0, help="Minimum size (KB)"),
    export: Optional[str] = typer.Option(None, help="Write results to JSON"),
):
    """Scan a directory and list groups of duplicate FLAC files."""
    folder = Path(directory).expanduser()
    if not folder.exists():
        console.print(f"❌ Directory not found: {directory}", style="red")
        raise typer.Exit(1)

    files = _gather_flac_files(folder, recursive)

    if min_size:
        min_bytes = min_size * 1024
        files = [f for f in files if f.stat().st_size >= min_bytes]

    if not files:
        console.print("❌ No FLAC files found", style="red")
        return

    console.print(f"🎵 Scanning {len(files)} FLAC files …")
    groups = _group_files_by(track(files, description="Analyzing files…"), by)
    duplicates = {k: v for k, v in groups.items() if len(v) > 1}

    if not duplicates:
        console.print("✅ No duplicates found!", style="green")
        return

    console.print(f"🔍 Found {len(duplicates)} duplicate group(s)")
    results: List[Dict[str, Any]] = []

    for i, (key, flist) in enumerate(duplicates.items(), 1):
        table = Table(show_header=True)
        table.add_column("Path")
        table.add_column("Title")
        table.add_column("Artist")
        table.add_column("Size")
        table.add_column("Duration")
        table.add_column("Modified")

        group_result: List[Dict[str, Any]] = []

        for fp in flist:
            meta = extract_flac_metadata(fp)
            if "error" in meta:
                table.add_row(str(fp), "Error", "Error", "-", "-", "-")
                group_result.append({"path": str(fp), "error": meta["error"]})
                continue

            tags = meta.get("tags", {})
            size_str = format_size(meta.get("size", 0))
            dur_str = format_duration(meta.get("length", 0))
            mtime_str = datetime.fromtimestamp(fp.stat().st_mtime).strftime(
                "%Y-%m-%d %H:%M"
            )

            table.add_row(
                str(fp),
                tags.get("title", "Unknown"),
                tags.get("artist", "Unknown"),
                size_str,
                dur_str,
                mtime_str,
            )
            group_result.append(
                {
                    "path": str(fp),
                    "title": tags.get("title", ""),
                    "artist": tags.get("artist", ""),
                    "size": size_str,
                    "duration": dur_str,
                    "modified": mtime_str,
                    "quality_score": get_audio_quality_score(meta),
                }
            )

        console.print(f"\n[bold]Group {i}[/bold] ({by}: {key})")
        console.print(table)
        results.append({"group_id": i, "key": key, "method": by, "files": group_result})

    if export:
        import json

        out = Path(export).expanduser()
        out.write_text(
            json.dumps(
                {
                    "scan_time": datetime.now().isoformat(),
                    "directory": directory,
                    "method": by,
                    "groups": results,
                },
                indent=2,
            )
        )
        console.print(f"✅ Results exported to {out}", style="green")


# --------------------------------------------------------------------------- #
# duplicates remove                                                           #
# --------------------------------------------------------------------------- #
@app.command("remove")
def remove_duplicates(
    directory: str = typer.Argument(..., help="Directory to scan"),
    by: str = typer.Option("hash", help="hash | title | filename | artist+title"),
    strategy: str = typer.Option(
        "interactive",
        help="interactive | keep-newest | keep-oldest | keep-highest-quality",
    ),
    dry_run: bool = typer.Option(True, help="Show actions only"),
    export_log: Optional[str] = typer.Option(None, help="Write log to JSON"),
):
    """Remove duplicate FLACs (optionally interactively)."""
    folder = Path(directory).expanduser()
    if not folder.exists():
        console.print(f"❌ Directory not found: {directory}", style="red")
        raise typer.Exit(1)

    files = _gather_flac_files(folder, recursive=True)
    if not files:
        console.print("❌ No FLAC files found", style="red")
        return

    console.print(f"🎵 Scanning {len(files)} FLAC files …")
    groups = _group_files_by(track(files, description="Analyzing files…"), by)
    duplicates = {k: v for k, v in groups.items() if len(v) > 1}

    if not duplicates:
        console.print("✅ No duplicates found!", style="green")
        return

    console.print(f"🔍 Found {len(duplicates)} duplicate group(s)")
    to_remove: List[Path] = []
    to_keep: List[Path] = []
    removal_log: List[Dict[str, str | int]] = []

    for i, (key, flist) in enumerate(duplicates.items(), 1):
        console.print(f"\n[bold]Group {i}[/bold] ({by}: {key})")

        if strategy == "interactive":
            for idx, fp in enumerate(flist, 1):
                meta = extract_flac_metadata(fp)
                if "error" in meta:
                    console.print(f"  {idx}. {fp} [red](unreadable)[/red]")
                    continue
                tags = meta.get("tags", {})
                console.print(
                    f"  {idx}. {fp}\n"
                    f"     Title: {tags.get('title', 'Unknown')} | "
                    f"Artist: {tags.get('artist', 'Unknown')} | "
                    f"Size: {format_size(meta.get('size', 0))} | "
                    f"Score: {get_audio_quality_score(meta) or '—'}"
                )

            choice = Prompt.ask(
                "Select file to keep "
                "(number, 'all' to keep all, 'auto' to select best)",
                default="1",
            )

            if choice.lower() == "all":
                to_keep.extend(flist)
                continue
            if choice.lower() == "auto":
                best = _select_best_file(flist, "keep-highest-quality")
            else:
                try:
                    best = flist[int(choice) - 1]
                except Exception:  # noqa: BLE001
                    console.print("Invalid choice – keeping all.", style="yellow")
                    to_keep.extend(flist)
                    continue
        else:
            best = _select_best_file(flist, strategy)

        if not best:
            console.print("Could not decide – keeping all.", style="yellow")
            to_keep.extend(flist)
            continue

        to_keep.append(best)
        doomed = [p for p in flist if p != best]
        to_remove.extend(doomed)
        for fp in doomed:
            removal_log.append(
                {
                    "group": i,
                    "key": key,
                    "removed": str(fp),
                    "kept": str(best),
                    "reason": strategy,
                }
            )

    console.print(f"\n📋 {len(to_remove)} file(s) will be removed")
    for fp in to_remove[:5]:
        console.print(f"  - {fp}")
    if len(to_remove) > 5:
        console.print(f"  … and {len(to_remove) - 5} more")

    if export_log:
        import json

        Path(export_log).write_text(
            json.dumps(
                {
                    "time": datetime.now().isoformat(),
                    "directory": directory,
                    "method": by,
                    "strategy": strategy,
                    "dry_run": dry_run,
                    "files_to_remove": [str(p) for p in to_remove],
                    "files_to_keep": [str(p) for p in to_keep],
                    "removal_log": removal_log,
                },
                indent=2,
            )
        )
        console.print(f"✅ Log written to {export_log}", style="green")

    if dry_run:
        console.print("\n🔍 DRY-RUN – nothing deleted", style="yellow")
        return

    if not Confirm.ask("⚠️  Continue and delete the files listed above?"):
        console.print("Cancelled.", style="yellow")
        return

    removed, errors = 0, []
    for fp in track(to_remove, description="Removing files…"):
        try:
            os.remove(fp)
            removed += 1
        except Exception as exc:  # noqa: BLE001
            errors.append((fp, str(exc)))

    if errors:
        console.print(f"⚠️ Removed {removed}; {len(errors)} error(s):", style="yellow")
        for fp, err in errors:
            console.print(f"  {fp}: {err}")
    else:
        console.print(f"✅ Removed {removed} duplicate file(s)", style="green")


if __name__ == "__main__":
    app()
