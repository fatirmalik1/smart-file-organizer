"""
app.py -- Smart File Organizer

Minimal Streamlit UI. Point it at ANY folder (not hardcoded) and it:
  1. Scans the folder and shows a preview of what it would do.
  2. On "Organize", moves every top-level file into Images/Documents/
     Videos/Archives/Other subfolders, in place, inside that same folder.
  3. Keeps a move-log so "Undo last run" can put everything back --
     useful for repeated rehearsal without manually re-messing the
     sample folder each time.

Run with:  streamlit run app.py
"""

from pathlib import Path

import streamlit as st

from organizer.mover import organize, scan, undo_last_run

st.set_page_config(page_title="Smart File Organizer", layout="wide")

st.title("Smart File Organizer")
st.caption(
    "Point this at any folder. It sorts files into Images / Documents / "
    "Videos / Archives / Other, in place, inside that same folder."
)

default_folder = str(Path(__file__).resolve().parent / "demo-inbox")
folder_str = st.text_input("Folder to organize", value=default_folder)
folder = Path(folder_str).expanduser()

col_scan, col_organize, col_undo = st.columns([1, 1, 1])
scan_clicked = col_scan.button("Scan")
organize_clicked = col_organize.button("Organize")
undo_clicked = col_undo.button("Undo last run")

if not folder.exists():
    st.error(f"Folder does not exist: {folder}")
elif not folder.is_dir():
    st.error(f"Not a folder: {folder}")
else:
    if undo_clicked:
        reversed_moves = undo_last_run(folder)
        if reversed_moves:
            st.success(f"Reversed {len(reversed_moves)} file(s) back to {folder}.")
        else:
            st.info("Nothing to undo.")

    if organize_clicked:
        moves = organize(folder)
        st.success(f"Organized {len(moves)} file(s).")

    # Always show a fresh preview of the folder's current top-level state.
    preview = scan(folder)
    st.subheader(f"{len(preview)} file(s) directly in this folder")
    if preview:
        st.table(preview)
    else:
        st.info("No top-level files here -- either it's empty or everything's already organized.")

    st.subheader("Current subfolders")
    subfolders = sorted(p.name for p in folder.iterdir() if p.is_dir())
    if subfolders:
        for name in subfolders:
            count = len(list((folder / name).iterdir()))
            st.write(f"**{name}/** -- {count} file(s)")
    else:
        st.write("None yet.")
