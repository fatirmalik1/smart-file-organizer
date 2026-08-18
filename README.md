# smart-file-organizer

Point it at any folder. It sorts the files inside into `Images/`,
`Documents/`, `Videos/`, `Archives/`, and `Other/` subfolders, in place.

Built for the Andela x Claude Code workshop, Session 4 (Sub-Agents &
Agentic Development). This repo is deliberately unfinished: see
`jira_ticket.md` for the real gap a live sub-agent pipeline (Planner ->
Coder -> Tester -> Reviewer -> Publisher) fixes during the session.

## Run the app

```bash
pip install -r requirements.txt
streamlit run app.py
```

Type any folder path into the text box (it defaults to `demo-inbox/`,
the sample messy folder shipped in this repo), click **Scan** to preview,
**Organize** to actually move files, **Undo last run** to put them back.

## Run the tests

```bash
pytest
```

These are green today. They cover the naive extension-based classifier on
well-formed files. They do NOT cover the tricky fixtures in `demo-inbox/`
(wrong extension, no extension, ambiguous content) -- that's the ticket.

## Reset the demo folder

```bash
./reset_demo.sh
```

Restores `demo-inbox/` to its pristine messy starting state from
`fixtures-pristine/`, and clears the undo log. Safe to run as many times as
you want during rehearsal.

## Regenerate the fixtures

```bash
python3 scripts/generate_fixtures.py
```

Only needed if the fixture set itself changes -- this writes real,
byte-valid JPEG/PNG/ZIP/MP4 content into `fixtures-pristine/`, including the
three "hard" cases the ticket is about.
