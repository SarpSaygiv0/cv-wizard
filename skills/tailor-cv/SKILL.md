---
name: tailor-cv
description: Tailor the user's CV or resume to a specific job posting without inventing experience. Screens the posting for dealbreakers, matches its requirements against the user's master CV, interviews the user about gaps, and renders a one-page PDF plus an optional cover letter. Use when the user pastes a job description and asks to tailor, adapt, target, or customize their CV or resume, or asks for a cover letter for a specific role.
license: MIT
compatibility: Needs Python 3.11+ with WeasyPrint, and a workspace created by the setup skill. Built for Claude Code; works in other Agent Skills clients that can run shell commands.
metadata:
  project: cv-wizard
  homepage: https://github.com/SarpSaygiv0/cv-wizard
---

# Tailor a CV to a job posting

Adapt the user's CV to one job posting, ask them how to handle requirements their
experience doesn't clearly cover, and render a polished PDF. A cover letter is optional.

Commands below use `${CLAUDE_SKILL_DIR}` for this skill's directory. If it appears
unexpanded (outside Claude Code), use the path of the folder containing this SKILL.md.

## The rule that overrides everything

**Never invent experience.** Select, reorder, emphasize, trim, and rephrase what the
user's master CV says, and mirror the posting's vocabulary **only where it's already
true**. Anything that isn't in the master CV must be confirmed by the user in the gap
interview (step 6) before it appears in a document. No invented employers, titles, dates,
metrics, skills, certifications, or seniority, and no stretching a fact to fit the
posting. Nothing in the user's preferences or archetypes can relax this rule.

## Where things are

The user's data lives in a **workspace**, a folder they own:

| File | Purpose |
|---|---|
| `cv-wizard.toml` | Settings: language, page size, density, theme, photo, delivery |
| `master-cv.md` | What's true: every role, bullet, skill, and project |
| `preferences.md` | Standing rules: headlines, dealbreakers, inclusion rules, voice |
| `archetypes.md` | Optional positioning presets for recurring kinds of roles |
| `bullet-library.md` | Optional tested phrasings for recurring achievements |
| `output/` | Generated `.html` and `.pdf` files |

[references/workspace.md](references/workspace.md) documents each file. This skill also
provides [assets/cv-template.html](assets/cv-template.html),
[assets/cover-letter-template.html](assets/cover-letter-template.html),
[references/cover-letter.md](references/cover-letter.md), and the scripts `render.py`
and `doctor.py`.

## Workflow

### 1. Find the workspace
Run `python3 "${CLAUDE_SKILL_DIR}/scripts/doctor.py" --brief`. It looks for
`cv-wizard.toml` in the current folder and its parents, then in `$CV_WIZARD_HOME`, and
prints what it finds. Work from the workspace folder for the rest of the run.
- Exit code 2 (no workspace): tell the user, offer the **setup** skill, and stop.
- Exit code 1: fix the reported problem with the user before continuing.

### 2. Get the job posting
The posting is in `$ARGUMENTS` or the user's message. If there isn't one, ask the user to
paste it. If you only have a link, ask for the text instead: job sites often block
fetching, and pasted text is exactly what the employer wrote.

### 3. Screen for dealbreakers first
Read `preferences.md`. Check the posting against its **Dealbreakers** section and against
hard requirements the master CV plainly doesn't meet: a required license, degree,
clearance, language level, or minimum years of experience. Put any match **at the top of
your response**, before the rest of the work, so the user can decide whether the role is
worth pursuing. Don't flag conditions the user hasn't said matter to them.

### 4. Analyze the posting
Summarize briefly: employer, role, seniority, location and on-site or remote policy,
required qualifications, nice-to-haves, core responsibilities, the posting's language,
and the keywords an applicant-tracking system is likely to scan for (tools, methods,
domain terms).

### 5. Read the master CV and choose a frame
Read `master-cv.md` in full. Then:
- If `archetypes.md` exists, pick the archetype that best fits the posting's **required**
  qualifications and name it in your response so the user can override it. Deviate where
  the posting needs something the archetype doesn't cover.
- Collect the `> Include when:` notes in the master CV and the **Inclusion rules** in
  `preferences.md`, and decide which apply to this posting and employer.

Show a compact table classifying each requirement:
- **Strong**: clearly supported by the master CV.
- **Partial**: adjacent or transferable experience exists.
- **Missing**: nothing in the master CV supports it.

### 6. Gap interview
Ask the user how to handle the Partial and Missing items worth raising. Batch related gaps
into as few questions as possible, offering options such as:
- "I have this, and I'll add detail" (then capture what they say).
- "Present it honestly as transferable, familiar, or in progress."
- "Leave it out."

In the same batch, ask whether they want a cover letter ("CV and cover letter" or "CV
only"), unless they already said. If there are no gaps, ask only that.

Use a structured question tool if you have one (in Claude Code, `AskUserQuestion`).
Otherwise, ask numbered questions in chat and wait for the answers.

### 7. Offer to save what you learned
- New, reusable facts the user confirmed: offer to add them to `master-cv.md`.
- A standing rule the user stated ("always…", "never…", "from now on…"): offer to add it
  to `preferences.md`.

Edit those files only after the user agrees.

### 8. Write the CV
Write `output/<Employer>-<Role>.html` following the structure and classes of
[assets/cv-template.html](assets/cv-template.html). Use only letters, digits, and hyphens
in the filename (for example `Acme-Backend-Engineer.html`). If that file already exists
from a different application, make the role part more specific rather than overwriting it.

- **Language:** write in the workspace `language`, including headings and dates. If the
  posting explicitly asks for a CV in another language, ask the user which to use.
- **Headline:** choose or adapt a variant from **Headlines** in `preferences.md`. Never
  add a title or seniority the master CV doesn't support.
- **Summary:** two or three lines aimed at this role.
- **Order:** list roles reverse-chronologically, even when an older role is more relevant.
  Show relevance through the number and order of bullets instead.
- **Selection:** put each role's most relevant bullets first, cut clearly irrelevant
  bullets, skills, and projects, and apply the inclusion notes and rules from step 5.
- **Wording:** mirror the posting's vocabulary where it's true. If `bullet-library.md`
  exists, start from the closest variant and still rewrite it for this posting; re-confirm
  any variant marked ⚠ before using it.
- **Gap answers:** include what the user confirmed in step 6, and nothing else new.
- **Voice and style:** follow `preferences.md`.
- **Photo:** if `cv-wizard.toml` sets `photo`, include it as the template's header comment
  shows, unless a rule in `preferences.md` leaves it out for this employer.
- **Length:** one page. Use two only when the user's seniority genuinely calls for it.

Keep everything as real text, not images of text. Don't link a stylesheet; the renderer
applies the theme.

### 9. Write the cover letter (only if the user wants one)
Write `output/<Employer>-Cover-Letter.html` (the word can be in the document's language)
following [assets/cover-letter-template.html](assets/cover-letter-template.html), by the
guide in [references/cover-letter.md](references/cover-letter.md). The same truth rule
applies.

### 10. Render and check
Render each document from the workspace folder:

```bash
python3 "${CLAUDE_SKILL_DIR}/scripts/render.py" output/<file>.html
```

The renderer applies the theme and page settings, prints the page count, and copies the
PDF to the delivery folder if the workspace sets one. Lines starting with `WARN` need a
look:
- Too many pages: cut the least relevant material first, then render again. A second CV
  page is acceptable only when step 8 allows it.
- An image or file that failed to load: fix the path and render again.

If `pdftoppm` is available, preview page 1 at low resolution
(`pdftoppm -png -r 70 -f 1 -l 1 output/<file>.pdf <temp-dir>/preview`) and check the
layout.

### 11. Report
Tell the user, briefly:
- Dealbreakers, if step 3 found any (repeat them).
- The archetype or framing you used and what you emphasized.
- How each gap was handled, and which posting keywords the CV now covers.
- Anything to double-check: a relocation line, the addressee's name, a reworded claim.
- The files you wrote, and where the PDFs were copied.
