# CV Wizard

Tailor your CV to every job posting, without inventing experience.

CV Wizard is a pair of [Agent Skills](https://agentskills.io), packaged as a Claude Code
plugin. Paste a job posting and it:

1. **Screens** the posting for your dealbreakers before doing any work.
2. **Matches** each requirement against your master CV: strong, partial, or missing.
3. **Asks you** how to handle the gaps instead of guessing.
4. **Writes** a one-page CV, plus a cover letter if you want one, in your language.
5. **Renders** a clean PDF that applicant-tracking systems can read, and copies it where
   you want it.

It only selects, reorders, and rephrases what's already in your master CV. Anything new
has to come from you.

## How it works

The engine and your data live apart:

- **This repository** holds the skills, templates, themes, and renderer. You install it as
  a plugin, and updates never touch your data.
- **Your workspace** is a folder you own, ideally a private git repository. It holds your
  master CV, your standing rules, and every document generated for you.

Two skills work on the workspace: `setup` creates it from your existing CV, and
`tailor-cv` tailors it to one posting at a time.

## Install

### Claude Code in the terminal

```
/plugin marketplace add SarpSaygiv0/cv-wizard
/plugin install cv-wizard@cv-wizard
```

### Claude desktop app

The `/plugin` commands above only work in the terminal. The desktop app installs plugins from a
plugin browser, which lists plugins from marketplaces you've already added, so add this one
first. If you have the `claude` command-line tool, run this in any terminal:

```bash
claude plugin marketplace add SarpSaygiv0/cv-wizard
```

Without it, add the same entry to `~/.claude/settings.json` yourself, merged into the existing
object:

```json
"extraKnownMarketplaces": {
  "cv-wizard": { "source": { "source": "github", "repo": "SarpSaygiv0/cv-wizard" } }
}
```

Then install the plugin:

1. In a local Code session, click **+** next to the prompt box, choose **Plugins**, then
   **Add plugin**.
2. Select **CV Wizard** and pick a scope. **User** makes it available in every project.
3. Start a new session, or type `/reload-plugins` in the prompt box, to load it.

To disable or remove it later, use **+** → **Plugins** → **Manage plugins**. In the quick start
below, open a Code session in your workspace folder instead of running `claude` there.

### Codex and other Agent Skills clients

Put both skill folders side by side in your agent's skills folder. For Codex:

```bash
git clone https://github.com/SarpSaygiv0/cv-wizard.git
mkdir -p ~/.agents/skills
ln -s "$PWD/cv-wizard/skills/setup" "$PWD/cv-wizard/skills/tailor-cv" ~/.agents/skills/
```

### PDF rendering

The renderer needs Python 3.11+ and [WeasyPrint](https://weasyprint.org).

macOS:

```bash
brew install pango
python3 -m pip install weasyprint
```

Debian or Ubuntu:

```bash
sudo apt install -y libpango-1.0-0 libpangoft2-1.0-0 libharfbuzz-subset0
python3 -m pip install weasyprint
```

If pip refuses because Homebrew or the system manages your Python, install WeasyPrint into a
virtual environment and start your agent with it activated. Optionally, install poppler
(`brew install poppler` or `sudo apt install poppler-utils`) so the skills can preview
pages. The setup skill checks all of this and tells you what's missing.

## Quick start

1. Make a folder for your workspace and start Claude Code in it:

   ```bash
   mkdir -p ~/cv && cd ~/cv && claude
   ```

2. Run `/cv-wizard:setup` and give it your current CV (PDF, DOCX, or pasted text). It asks a
   few questions, writes the workspace, and renders a test PDF.
3. For each job, run `/cv-wizard:tailor-cv` and paste the posting.

In Codex, the skills are `$setup` and `$tailor-cv`. Documents land in `output/` as editable
`.html` and finished `.pdf`. To use your workspace from any folder, set `CV_WIZARD_HOME` to
its path.

## Your workspace

| File | What it holds |
|---|---|
| `cv-wizard.toml` | Language, page size, density, theme, accent color, photo, and where to copy finished PDFs |
| `master-cv.md` | Every role, achievement, skill, and project, including the ones you rarely use. `> Include when:` notes mark items that only fit some jobs |
| `preferences.md` | Standing rules: headline variants, dealbreakers, inclusion rules, voice and style |
| `archetypes.md` | Optional presets for the kinds of roles you apply to most |
| `bullet-library.md` | Optional tested phrasings for recurring achievements |

The full format is in
[`skills/tailor-cv/references/workspace.md`](skills/tailor-cv/references/workspace.md), and
[`examples/`](examples/) has two complete, fictional workspaces.

## Keep your workspace private

A workspace holds your contact details, your full work history, and a record of every
company you've applied to.

- Keep it in a **private** repository, or in no repository at all.
- Don't create it inside a clone or fork of this repository.
- After each run, tailor-cv offers to add new facts to your master CV. Review those edits
  like any other change to your CV.

## Change the look

In `cv-wizard.toml`:

- `page_size = "Letter"` for the US and Canada; `"A4"` everywhere else.
- `density = "compact"` for tighter spacing on dense one-page CVs.
- `accent_color = "#7a2e1f"` to recolor your name and the headings.
- `custom_css = "style.css"` to apply your own CSS on top of the theme.

Themes live in [`skills/tailor-cv/assets/themes/`](skills/tailor-cv/assets/themes/).

## Render by hand

After editing an HTML file in `output/`:

```bash
python3 path/to/cv-wizard/skills/tailor-cv/scripts/render.py output/Acme-Backend-Engineer.html
```

## Develop

```bash
claude --plugin-dir .
python3 -m unittest discover -s tests -v
claude plugin validate .
```

`--plugin-dir` loads your working copy for one session (run `/reload-plugins` after edits).
The tests render every example document. Contributor rules are in [AGENTS.md](AGENTS.md);
the most important one is that real personal data never goes in this repository.

## License

[MIT](LICENSE)
