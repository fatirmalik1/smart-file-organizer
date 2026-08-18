"""
Baseline tests. These are GREEN today, before the Jira ticket's fix.
They cover the naive extension-based classifier on well-formed files --
i.e. files whose extension can be trusted. They intentionally do NOT
cover the tricky fixtures in demo-inbox/ (wrong extension, no extension,
ambiguous content) -- writing those tests is the Tester agent's job.
"""

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
