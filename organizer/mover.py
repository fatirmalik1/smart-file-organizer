"""
organizer/mover.py

Physically organizes a folder: for every file directly inside `folder`
(not already sitting in one of the category subfolders, and not the log
file itself), compute its category via classify.classify() and move it
into a same-named subfolder, creating the subfolder if needed.

Writes a JSON move-log (`.organize_log.json`) inside the target folder so
a run can be undone -- this makes it safe to re-run the same demo folder
over and over during rehearsal without manually re-messing it each time.
"""

import json
import shutil
from datetime import datetime
from pathlib import Path

from organizer.classify import CATEGORIES, classify

LOG_FILENAME = ".organize_log.json"


def _log_path(folder: Path) -> Path:
    return folder / LOG_FILENAME


def scan(folder: Path):
    """Preview only -- does not move anything. Returns a list of dicts:
    {"name": str, "category": str}, one per file directly inside `folder`
    (skips subfolders and the log file)."""
    results = []
    for entry in sorted(folder.iterdir()):
        if entry.is_dir() or entry.name == LOG_FILENAME:
            continue
        results.append({"name": entry.name, "category": classify(entry)})
    return results


def organize(folder: Path):
    """Moves every top-level file in `folder` into its category
    subfolder. Returns the list of moves performed, and writes/appends to
    the move-log so this run can be undone."""
    moves = []
    for entry in sorted(folder.iterdir()):
        if entry.is_dir() or entry.name == LOG_FILENAME:
            continue
        category = classify(entry)
        dest_dir = folder / category
        dest_dir.mkdir(exist_ok=True)
        dest = dest_dir / entry.name
        shutil.move(str(entry), str(dest))
        moves.append({"from": str(dest.relative_to(folder)), "to": entry.name})

    log_path = _log_path(folder)
    existing = []
    if log_path.exists():
        existing = json.loads(log_path.read_text())
    existing.append({"timestamp": datetime.now().isoformat(), "moves": moves})
    log_path.write_text(json.dumps(existing, indent=2))
    return moves


def undo_last_run(folder: Path):
    """Reverses the most recent organize() run using the move-log. Safe
    to call repeatedly during rehearsal -- each call pops one run off the
    log."""
    log_path = _log_path(folder)
    if not log_path.exists():
        return []
    history = json.loads(log_path.read_text())
    if not history:
        return []
    last_run = history.pop()
    reversed_moves = []
    for move in last_run["moves"]:
        src = folder / move["from"]
        dst = folder / move["to"]
        if src.exists():
            shutil.move(str(src), str(dst))
            reversed_moves.append(move)
    for category in CATEGORIES:
        cat_dir = folder / category
        if cat_dir.exists() and not any(cat_dir.iterdir()):
            cat_dir.rmdir()
    log_path.write_text(json.dumps(history, indent=2))
    return reversed_moves
