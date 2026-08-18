#!/usr/bin/env python3
"""
scripts/generate_fixtures.py

Builds fixtures-pristine/ -- the messy folder as it should look before
every rehearsal or live run. reset_demo.sh copies this into demo-inbox/.

Regenerate with:  python3 scripts/generate_fixtures.py

Fixture set (9 files):

Well-formed (correctly classified even by the naive baseline -- these
are the regression cases the fix must not break):
  beach_photo.jpg        real JPEG bytes            -> Images
  team_offsite.png       real PNG bytes             -> Images
  project_plan.docx      real docx (zip) bytes      -> Documents
  budget_notes.txt       real plain text            -> Documents
  demo_clip.mp4          minimal real mp4 header    -> Videos
  backup.zip             real zip archive           -> Archives

Tricky (wrong under the naive baseline -- these are what the ticket
fixes):
  invoice_scan.pdf       actually PNG bytes, misleading .pdf extension
                         -> naive baseline: Documents (wrong)
                         -> after fix: Images (content wins)
  IMG_4471               no extension at all, actually a real JPEG
                         -> naive baseline: Other (wrong)
                         -> after fix: Images (content wins)
  mystery_file           no extension, genuinely unrecognizable bytes
                         -> naive baseline: Other
                         -> after fix: _needs_review (not a guess)
"""

import io
import zipfile
from pathlib import Path

from PIL import Image

ROOT = Path(__file__).resolve().parent.parent
PRISTINE = ROOT / "fixtures-pristine"


def _jpeg_bytes(color=(200, 120, 60)) -> bytes:
    buf = io.BytesIO()
    Image.new("RGB", (32, 32), color).save(buf, format="JPEG")
    return buf.getvalue()


def _png_bytes(color=(60, 120, 200)) -> bytes:
    buf = io.BytesIO()
    Image.new("RGB", (32, 32), color).save(buf, format="PNG")
    return buf.getvalue()


def _zip_bytes(inner_name="hello.txt", inner_content=b"hello from inside the archive") -> bytes:
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w") as zf:
        zf.writestr(inner_name, inner_content)
    return buf.getvalue()


def _mp4_bytes() -> bytes:
    # Minimal ISO-BMFF "ftyp" box header -- enough for a magic-byte sniffer
    # to recognize as MP4-family, not a playable video.
    return b"\x00\x00\x00\x18ftypmp42\x00\x00\x00\x00mp42isom" + b"\x00" * 32


def main():
    if PRISTINE.exists():
        import shutil

        shutil.rmtree(PRISTINE)
    PRISTINE.mkdir(parents=True)

    # -- Well-formed --
    (PRISTINE / "beach_photo.jpg").write_bytes(_jpeg_bytes((235, 200, 120)))
    (PRISTINE / "team_offsite.png").write_bytes(_png_bytes((120, 180, 235)))
    (PRISTINE / "project_plan.docx").write_bytes(_zip_bytes("word/document.xml", b"<xml>fake docx body</xml>"))
    (PRISTINE / "budget_notes.txt").write_text(
        "Q3 budget notes:\n- Travel is over by 12%.\n- Everything else on track.\n"
    )
    (PRISTINE / "demo_clip.mp4").write_bytes(_mp4_bytes())
    (PRISTINE / "backup.zip").write_bytes(_zip_bytes("readme.txt", b"old project backup"))

    # -- Tricky: misleading extension (actually a PNG, saved as .pdf) --
    (PRISTINE / "invoice_scan.pdf").write_bytes(_png_bytes((250, 250, 250)))

    # -- Tricky: no extension at all (actually a real JPEG) --
    (PRISTINE / "IMG_4471").write_bytes(_jpeg_bytes((80, 80, 80)))

    # -- Tricky: no extension, genuinely unrecognizable / not valid text --
    # Invalid UTF-8 (stray continuation/never-valid bytes) so it fails a
    # text decode, and no recognizable magic-byte signature either.
    (PRISTINE / "mystery_file").write_bytes(bytes([0x80, 0x81, 0xfe, 0xff]) * 16)

    print(f"Wrote {len(list(PRISTINE.iterdir()))} fixture files to {PRISTINE}")


if __name__ == "__main__":
    main()
