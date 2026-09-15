# Contributor guide

This repository is the public cv-wizard engine: skills, templates, themes, and the renderer.
It must never contain anyone's real CV data.

## Layout

- `skills/tailor-cv/`: the tailoring workflow (`SKILL.md`), `references/`, `assets/`
  (templates, themes, workspace starter files), and `scripts/` (`render.py`, `doctor.py`,
  and the shared `cvwlib.py`).
- `skills/setup/`: onboarding. It uses tailor-cv's references, assets, and scripts through
  the sibling path, so the two skills ship together.
- `examples/`: fictional workspaces that document the formats and serve as test fixtures.
- `tests/`: run `python3 -m unittest discover -s tests -v`.
- `.claude-plugin/`: plugin and marketplace manifests.

## Rules

- **No real personal data.** Examples use made-up people, employers, and schools,
  `example.com` addresses, and placeholder phone numbers.
- **User data belongs in the workspace**, never in the skill folders. Installed plugins are
  copied into a cache and replaced on every update.
- **Behavior everyone needs goes in the skills; one person's preferences go in their
  `preferences.md`.** If only one user would want a rule, it's a preference.
- **Keep skills portable.** Frontmatter uses only Agent Skills fields: `name`,
  `description`, `license`, `compatibility`, `metadata`, `allowed-tools`. Anything
  Claude-Code-specific in a skill body (`${CLAUDE_SKILL_DIR}`, `$ARGUMENTS`,
  `AskUserQuestion`) needs a fallback other agents can follow.
- **Scripts use the standard library plus WeasyPrint**, nothing else.
- Keep each `SKILL.md` under 500 lines; move detail into `references/`.
- After changing templates, themes, or examples, run the tests. Every example document must
  still fit on one page.
