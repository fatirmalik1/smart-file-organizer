"""
organizer/classify.py

Baseline (pre-ticket) behavior: classify a file purely by its extension,
using a static extension -> category map. Anything with an unknown or
missing extension falls into "Other".

This is deliberately naive. It works fine for well-behaved files, but it
trusts the extension even when the extension is wrong, missing, or
misleading -- which is exactly the gap the Jira ticket asks us to close.
See jira_ticket.md in the repo root for the full ticket text.
"""

from pathlib import Path

CATEGORIES = ["Images", "Documents", "Videos", "Archives", "Other"]

EXTENSION_MAP = {
    ".jpg": "Images",
    ".jpeg": "Images",
    ".png": "Images",
    ".gif": "Images",
    ".docx": "Documents",
    ".pdf": "Documents",
    ".txt": "Documents",
    ".md": "Documents",
    ".mp4": "Videos",
    ".mov": "Videos",
    ".zip": "Archives",
    ".tar": "Archives",
    ".gz": "Archives",
}


def classify_by_extension(path: Path) -> str:
    """Naive baseline: trust the file extension. Unknown or missing
    extensions default to "Other". This is the function the ticket wants
    extended with content-based detection -- do not delete it outright,
    the fallback/extension-trusted path is still useful once content
    sniffing is added."""
    return EXTENSION_MAP.get(path.suffix.lower(), "Other")


def classify(path: Path) -> str:
    """Current entry point used by the app. Today this is just an alias
    for classify_by_extension -- this is the seam a future implementation
    should extend with real content sniffing."""
    return classify_by_extension(path)
