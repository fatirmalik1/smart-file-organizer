# Jira ticket (local reference copy)

Keep this in the repo as a fallback: if the live Jira MCP call fails or is
slow mid-demo, read this aloud / paste it in instead of losing the moment.

---

**Summary:** Organizer misfiles renamed and extensionless files

**Description:**

The file organizer currently trusts the file extension, which breaks when
a file has been renamed or has no extension at all.

Add content-based type detection -- sniff the actual file signature, not
just the extension -- so files are still classified correctly even with a
wrong or missing extension.

If content-based detection can't confidently determine a type, don't
guess: move the file to `_needs_review/` instead of silently leaving it
in `Other/`.

**Acceptance criteria:**
- A file with a misleading extension (e.g. an image saved with a `.pdf`
  name) is filed by its real content type, not its extension.
- A file with no extension at all is still classified correctly when its
  content matches a known type.
- A file whose content can't be confidently identified goes to
  `_needs_review/`, not `Other/`.
- Existing well-formed files (trustworthy extensions) keep working
  exactly as before -- don't regress the baseline test suite.

**Labels:** bug, file-organizer
