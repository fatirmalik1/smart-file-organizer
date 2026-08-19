"""
organizer/classify.py

Baseline (pre-ticket) behavior: classify a file purely by its extension,
using a static extension -> category map. Anything with an unknown or
missing extension falls into "Other".

This is deliberately naive. It works fine for well-behaved files, but it
trusts the extension even when the extension is wrong, missing, or
misleading -- which is exactly the gap the Jira ticket asks us to close.
See jira_ticket.md in the repo root for the full ticket text.

KAN-5: content-based type detection. `classify()` now sniffs the file's
actual byte signature first, and only falls back to the extension when
sniffing can't confidently determine a type. When sniffing comes up empty
AND there's no extension to fall back on either, the file goes to
"_needs_review" instead of being silently dumped in "Other".
"""

import zipfile
from pathlib import Path

CATEGORIES = ["Images", "Documents", "Videos", "Archives", "Other", "_needs_review"]

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


def _read_header(path: Path, size: int = 32) -> bytes:
    """Read the first `size` bytes of a file for signature checks. Returns
    b"" if the file can't be read, so callers fall through to the
    extension-fallback path instead of raising."""
    try:
        with open(path, "rb") as f:
            return f.read(size)
    except OSError:
        return b""


def _looks_like_docx(path: Path) -> bool:
    """A ZIP-family file is a real .docx if it actually opens as a zip and
    its namelist looks like an Office Open XML document. A `word/`-prefixed
    entry alone is sufficient signal (some real-world docx files omit
    `[Content_Types].xml` from the namelist we see, e.g. when built by hand
    or minimally)."""
    try:
        with zipfile.ZipFile(path) as zf:
            names = zf.namelist()
    except (zipfile.BadZipFile, OSError):
        return False
    return "[Content_Types].xml" in names or any(
        name.startswith("word/") for name in names
    )


def _sniff_by_content(path: Path) -> str | None:
    """Try to determine the file's category from its actual bytes,
    independent of its extension. Returns None if sniffing is
    inconclusive, so the caller can fall back to the extension."""
    header = _read_header(path)

    # Images
    if header[:3] == b"\xff\xd8\xff":
        return "Images"
    if header[:8] == b"\x89PNG\r\n\x1a\n":
        return "Images"
    if header[:6] in (b"GIF87a", b"GIF89a"):
        return "Images"

    # Videos (ISO-BMFF: MP4/MOV)
    if header[4:8] == b"ftyp":
        return "Videos"

    # Documents / Archives (ZIP-family, needs disambiguation)
    if header[:4] == b"PK\x03\x04" or header[:4] == b"PK\x05\x06":
        try:
            with zipfile.ZipFile(path):
                pass
        except (zipfile.BadZipFile, OSError):
            return None  # inconclusive -- truncated/fake zip bytes
        return "Documents" if _looks_like_docx(path) else "Archives"

    return None


def _classify_with_fallback(path: Path) -> str:
    """Extension-fallback step used once content-sniffing has failed to
    find a positive signature match. Distinguishes "no signal at all"
    (no extension either -> _needs_review) from "extension present but
    unrecognized" (-> Other, same as today's baseline behavior)."""
    ext = path.suffix.lower()
    if ext in EXTENSION_MAP:
        return EXTENSION_MAP[ext]
    if ext == "":
        return "_needs_review"
    return "Other"


def classify(path: Path) -> str:
    """Current entry point used by the app. Tries content-based sniffing
    first (so a misleading or missing extension doesn't fool it), then
    falls back to the trusted-extension path, and finally to
    "_needs_review" when there's no signal at all."""
    sniffed = _sniff_by_content(path)
    if sniffed is not None:
        return sniffed
    return _classify_with_fallback(path)
