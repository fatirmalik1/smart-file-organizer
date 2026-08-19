"""
Baseline tests. These are GREEN today, before the Jira ticket's fix.
They cover the naive extension-based classifier on well-formed files --
i.e. files whose extension can be trusted. They intentionally do NOT
cover the tricky fixtures in demo-inbox/ (wrong extension, no extension,
ambiguous content) -- writing those tests is the Tester agent's job.
"""

import zipfile
from pathlib import Path

from organizer.classify import classify


def test_jpg_is_image(tmp_path):
    f = tmp_path / "beach_photo.jpg"
    f.write_bytes(b"\xff\xd8\xff\xe0fake-jpeg-bytes")
    assert classify(f) == "Images"


def test_png_is_image(tmp_path):
    f = tmp_path / "team_offsite.png"
    f.write_bytes(b"\x89PNG\r\n\x1a\nfake-png-bytes")
    assert classify(f) == "Images"


def test_docx_is_document(tmp_path):
    f = tmp_path / "project_plan.docx"
    f.write_bytes(b"PK\x03\x04fake-docx-bytes")
    assert classify(f) == "Documents"


def test_txt_is_document(tmp_path):
    f = tmp_path / "budget_notes.txt"
    f.write_text("Q3 budget notes: travel is over by 12%.")
    assert classify(f) == "Documents"


def test_mp4_is_video(tmp_path):
    f = tmp_path / "demo_clip.mp4"
    f.write_bytes(b"\x00\x00\x00\x18ftypmp42fake-mp4-bytes")
    assert classify(f) == "Videos"


def test_zip_is_archive(tmp_path):
    f = tmp_path / "backup.zip"
    f.write_bytes(b"PK\x03\x04fake-zip-bytes")
    assert classify(f) == "Archives"


def test_unknown_extension_is_other(tmp_path):
    f = tmp_path / "notes.xyz123"
    f.write_text("whatever")
    assert classify(f) == "Other"


# --- KAN-5: content-based detection ------------------------------------
#
# The tests above only ever exercise files whose extension can be
# trusted. The ones below cover the ticket's actual acceptance criteria:
# a wrong extension, a missing extension, and content that can't be
# confidently identified at all.


def test_misleading_extension_png_saved_as_pdf_is_image(tmp_path):
    """Content says PNG, extension says .pdf -- real content wins."""
    f = tmp_path / "invoice_scan.pdf"
    f.write_bytes(b"\x89PNG\r\n\x1a\nfake-png-bytes-with-a-lying-extension")
    assert classify(f) == "Images"


def test_misleading_extension_jpeg_saved_as_txt_is_image(tmp_path):
    """Second misleading-extension case with a different real/claimed
    type pairing, so we're not only exercising one signature branch."""
    f = tmp_path / "definitely_a_report.txt"
    f.write_bytes(b"\xff\xd8\xff\xe0fake-jpeg-bytes-in-a-text-file")
    assert classify(f) == "Images"


def test_no_extension_jpeg_is_image(tmp_path):
    """No extension at all, but the content matches a known signature --
    should still be classified correctly, not dumped in Other."""
    f = tmp_path / "IMG_4471"
    f.write_bytes(b"\xff\xd8\xff\xe0fake-jpeg-bytes-no-extension")
    assert classify(f) == "Images"


def test_no_extension_mp4_is_video(tmp_path):
    """A second no-extension case covering a different signature family
    (ISO-BMFF/mp4) to make sure the fix isn't image-specific."""
    f = tmp_path / "demo_clip"
    f.write_bytes(b"\x00\x00\x00\x18ftypmp42fake-mp4-bytes-no-extension")
    assert classify(f) == "Videos"


def test_unrecognizable_content_no_extension_needs_review(tmp_path):
    """This is the acceptance criterion most likely to be missed: content
    that can't be confidently identified must land in _needs_review/,
    NOT silently in Other/."""
    f = tmp_path / "mystery_file"
    # No extension, and bytes that don't match any known signature.
    f.write_bytes(b"\x80\x81\xfe\xff" * 8)
    result = classify(f)
    assert result == "_needs_review"
    assert result != "Other"


def test_real_docx_zip_with_misleading_extension_is_document(tmp_path):
    """A genuine Office Open XML zip (not just PK magic bytes) saved with
    a non-.docx extension should still be recognized as a Document via
    the docx-disambiguation path, not just the top-level PK sniff."""
    f = tmp_path / "renamed_report.bin"
    with zipfile.ZipFile(f, "w") as zf:
        zf.writestr("[Content_Types].xml", "<Types/>")
        zf.writestr("word/document.xml", "<document/>")
    assert classify(f) == "Documents"


def test_real_plain_zip_with_misleading_extension_is_archive(tmp_path):
    """A genuine zip archive that is NOT an Office document, saved with a
    misleading image extension, should be classified as an Archive, not
    a Document -- confirms the docx/zip disambiguation goes both ways."""
    f = tmp_path / "photos.jpg"
    with zipfile.ZipFile(f, "w") as zf:
        zf.writestr("readme.txt", "just a plain zip, not a docx")
    assert classify(f) == "Archives"


def test_truncated_zip_bytes_with_docx_extension_still_documents(tmp_path):
    """Regression guard: the existing baseline behavior for a trusted
    extension paired with fake/truncated zip bytes (not a real zip, so
    sniffing is inconclusive) must keep falling back to the extension,
    exactly as before the fix."""
    f = tmp_path / "project_plan.docx"
    f.write_bytes(b"PK\x03\x04fake-docx-bytes")
    assert classify(f) == "Documents"
