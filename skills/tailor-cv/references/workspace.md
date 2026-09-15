# Workspace reference

A workspace is a folder the user owns, ideally a private git repository, that holds
everything personal. The skills read and edit it; they never keep user data anywhere else.

```
my-cv/
├── cv-wizard.toml       settings (required)
├── master-cv.md         what's true (required)
├── preferences.md       standing rules (recommended)
├── archetypes.md        positioning presets (optional)
├── bullet-library.md    tested phrasings (optional)
├── photo.jpg            headshot (optional)
└── output/              generated documents
```

`scripts/doctor.py` and `scripts/render.py` find the workspace by walking up from the
current folder (or the HTML file being rendered) to the nearest `cv-wizard.toml`, then fall
back to the `CV_WIZARD_HOME` environment variable.

## cv-wizard.toml

Only what the renderer and the file layout need. Rules to reason about belong in
`preferences.md`.

| Key | Default | Meaning |
|---|---|---|
| `language` | `"en"` | Language of generated documents, as a tag such as `en`, `en-US`, `de`, `tr` |
| `page_size` | `"A4"` | `"A4"` or `"Letter"` |
| `density` | `"normal"` | `"normal"`, or `"compact"` for tighter spacing and slightly smaller type |
| `theme` | `"classic"` | A folder under `assets/themes/` |
| `accent_color` | theme's | Hex color for the name and headings, such as `"#1f3a5f"` |
| `custom_css` | none | CSS file in the workspace, applied after the theme |
| `photo` | none | Headshot image, relative to the workspace |
| `[delivery] copy_to` | none | Folder that receives a copy of every rendered PDF, such as `"~/Downloads"` |
| `[delivery] cv_filename` | `"CV.pdf"` | Stable filename for the CV copy |
| `[delivery] cover_letter_filename` | `"Cover_Letter.pdf"` | Stable filename for the cover-letter copy |

## master-cv.md

The superset of the user's experience. Usual sections, in order: Contact, Summary, Skills,
Experience, Projects, Education, Certifications, Languages. Add others as needed, such as
Internships, Publications, Volunteering, or Profile & Working Style. Section names may be
in the user's language.

Each role:

```markdown
### <Title> — <Organization>
- **Dates:** Mar 2021 – Present
- **Location:** City, Country
- <Achievement, with a concrete result where one exists>
```

**Blockquote notes are instructions, not content.** Never copy them into a document.
- `> Include when: <condition>` under an item: use the item only when the condition holds
  for this posting or employer.
- `> Tailoring note: <text>`: general guidance about a section or item.

## preferences.md

Plain-language rules under fixed headings. Empty sections are fine; the rules themselves
can be in any language.

- **Headlines**: the neutral headline and the role-specific variants tailoring may use.
- **Dealbreakers**: posting conditions to flag at the top before any work, such as
  relocation, sponsorship, clearance, language levels, licenses, or minimum years.
- **Inclusion rules**: items or formats that depend on the posting or employer, such as a
  project that only fits some roles or a date format that depends on the employer's country.
- **Voice & style**: tone, person and tense, how to state years of experience, words to
  avoid.
- **Cover letters**: anything beyond `references/cover-letter.md`.
- **Other**: everything else.

Precedence: the no-fabrication rule first, then `preferences.md`, then the skill's
defaults.

## archetypes.md (optional)

Presets for the kinds of roles the user applies to repeatedly. Each fixes decisions a run
would otherwise re-derive; none of them is a pre-written CV.

```markdown
## A1 · Backend / APIs
**Use when:** the required list leads with backend services and APIs.
- **Headline:** Backend Software Engineer · <2–3 posting keywords>
- **Lead with:** <the role whose substance matters most>
- **Emphasize:** <achievements or themes in scope>
- **Skills lines:** <which categories, in what order>
- **Projects:** <which project, or none>
- **Watch:** <claims to avoid, pitfalls>
```

## bullet-library.md (optional)

Tested phrasings for each achievement, usually harvested from earlier tailored CVs. Group
them by role and theme, and keep several framings of the same fact where postings differ.
Mark any variant that rests on a fact not yet in `master-cv.md` with ⚠, and re-confirm it
with the user before using it.

## output/

`<Employer>-<Role>.html` and `.pdf` for CVs, `<Employer>-Cover-Letter.html` and `.pdf` for
cover letters. Each HTML file declares its kind with
`<meta name="cv-wizard:kind" content="cv" />` or `content="cover-letter"`, so filenames can
be in any language. Keep the HTML next to the PDF so it can be edited and re-rendered.
