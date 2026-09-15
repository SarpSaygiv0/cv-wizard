---
name: setup
description: Create a cv-wizard workspace, the private folder holding a person's master CV, preferences, and generated documents. Imports an existing CV or resume (PDF, DOCX, or pasted text), interviews the user to make it complete and truthful, records their standing preferences, and checks that PDF rendering works. Use when someone wants to start using cv-wizard, set up or import their CV or resume for tailoring, or when the tailor-cv skill can't find a workspace.
license: MIT
compatibility: Needs Python 3.11+ with WeasyPrint, and the tailor-cv skill installed next to this one (it provides the templates, format reference, and scripts).
metadata:
  project: cv-wizard
  homepage: https://github.com/SarpSaygiv0/cv-wizard
---

# Set up a cv-wizard workspace

A workspace is a folder the user owns that holds everything personal: `cv-wizard.toml`,
`master-cv.md`, `preferences.md`, an optional `archetypes.md`, and `output/`. This skill
creates one; the **tailor-cv** skill uses it for every job posting.

This skill uses files from its sibling, tailor-cv. Paths below use `${CLAUDE_SKILL_DIR}`
for this skill's directory; if it appears unexpanded (outside Claude Code), use the path
of the folder containing this SKILL.md.

- Format reference (read it before writing any workspace file):
  `${CLAUDE_SKILL_DIR}/../tailor-cv/references/workspace.md`
- Starter files: `${CLAUDE_SKILL_DIR}/../tailor-cv/assets/workspace-template/`
- CV template: `${CLAUDE_SKILL_DIR}/../tailor-cv/assets/cv-template.html`
- Doctor: `python3 "${CLAUDE_SKILL_DIR}/../tailor-cv/scripts/doctor.py"`
- Renderer: `python3 "${CLAUDE_SKILL_DIR}/../tailor-cv/scripts/render.py"`

**Record only what the user tells you or what their existing CV says.** Don't embellish,
estimate metrics, or fill gaps with plausible guesses. Batch your questions. Use a
structured question tool if you have one (in Claude Code, `AskUserQuestion`); otherwise
ask numbered questions in chat and wait for the answers.

## 1. Choose the folder
- Run the doctor with `--brief`. If it finds a workspace, tell the user and offer to
  review or update it instead of starting over.
- Otherwise suggest the current folder if it's empty or clearly meant for this, or a new
  folder such as `~/cv`. Confirm before creating anything.
- Recommend a **private** git repository or no repository: the workspace will hold their
  contact details, work history, and a record of where they've applied. Never create it
  inside a clone of the cv-wizard repository.

## 2. Check rendering
Run the doctor without `--brief`. If WeasyPrint fails, show the user the `HINT` lines,
help them install it, and run the doctor again. You can keep collecting CV content while
they install, but don't finish setup until the test render passes.

## 3. Import the current CV
Ask for their current CV: a file (PDF, DOCX, Markdown, or text), pasted text, or a PDF
export of their LinkedIn profile. To read it:
- PDF: read it directly if you can, otherwise `pdftotext -layout <file> -`.
- DOCX: `textutil -convert txt -stdout <file>` on macOS, or `pandoc -t plain <file>`. If
  neither works, ask the user to paste the text.

With no existing CV, build the master CV from the questions in step 4.

Draft `master-cv.md` from the starter file, keeping every fact exactly as the source
states it. Include everything: all roles, internships, projects, education, certificates,
and languages. Tailoring can only choose from what's here, so more is better.

## 4. Fill the gaps
Summarize what you imported, then ask about what matters most for tailoring:
- Bullets without a result: is there a scale or outcome (users, volume, money or time
  saved, before and after)? Accept "I don't know" and keep the bullet as it is.
- Missing dates, locations, or titles.
- Tools, methods, and domain knowledge from each role that the CV leaves out.
- Achievements that never made it onto the CV: launches, promotions, mentoring, awards.
- Items that only fit some jobs. Record them with `> Include when:` notes.

Write the answers into `master-cv.md`. Keep it to about two rounds of questions; the user
can add more later, and tailor-cv offers to save new facts after every run.

## 5. Record preferences and settings
Ask, in one or two batches:
- **Target roles:** the kinds of roles they apply to, and a headline for each
  (→ **Headlines**).
- **Dealbreakers:** conditions to flag before any work, such as location or relocation,
  work authorization or sponsorship, clearance, language requirements, licenses, or
  experience minimums (→ **Dealbreakers**).
- **Conventions:** document language; page size (Letter is usual in the US and Canada, A4
  almost everywhere else); whether to include a photo (expected in some countries, such as
  Germany or Turkey, and usually left out in the US and UK); how to state years of
  experience; tone and wording rules (→ `cv-wizard.toml` and **Voice & style**).
- **Delivery:** whether every finished PDF should also be copied to a fixed folder, such
  as Downloads, under a stable filename (→ `[delivery]`).

If they apply to two or more distinct kinds of roles, offer to draft `archetypes.md` with a
preset for each.

## 6. Write the workspace
From the starter files, create:
- `cv-wizard.toml`, with their settings (leave unused options commented out).
- `master-cv.md`, from steps 3 and 4.
- `preferences.md`, keeping every heading even when a section is empty.
- `archetypes.md`, only if they wanted it.
- The photo, if they gave you one: copy it into the workspace and set `photo`.
- A `.gitignore` containing `output/`, if the folder is or will be a git repository.

## 7. Test render
Write `output/Master-CV.html` from the CV template with the **untailored** master CV, in
the workspace language, and render it with `--no-copy` so it doesn't replace a real
application in the delivery folder. It may run past one page; that's fine here. If
`pdftoppm` is available, preview page 1 and check the layout, then fix any problems.

## 8. Hand over
Tell the user:
- Where the workspace is and what each file does.
- That `master-cv.md` is the only source tailoring uses, so it should stay complete and
  true.
- How to tailor: from the workspace folder, run tailor-cv (in Claude Code,
  `/cv-wizard:tailor-cv`) and paste a job posting. Setting `CV_WIZARD_HOME` to the
  workspace path makes it work from any folder.
