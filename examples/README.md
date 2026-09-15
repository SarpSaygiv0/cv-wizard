# Examples

Two complete, fictional workspaces. They document the file formats and double as test
fixtures: the tests render every document in their `output/` folders and require each one
to fit on a single page.

| Workspace | Shows |
|---|---|
| [`jordan-avery/`](jordan-avery/) | US software engineer, English: Letter paper, archetypes, and a posting with a Kubernetes gap the CV doesn't paper over |
| [`deniz-yilmaz/`](deniz-yilmaz/) | Civil engineer in Turkey, Turkish documents: A4, photo, compact density, accent color, internships in their own section, and a cover letter whose filename isn't English |

Each workspace has a `jobs/` folder with the posting its `output/` documents were tailored
to. That folder isn't part of the workspace format; it's here so you can compare input and
output.

Everything here is made up: people, employers, schools, numbers, `example.com` addresses,
and placeholder phone numbers. Keep it that way.

Render one:

```bash
python3 skills/tailor-cv/scripts/render.py examples/deniz-yilmaz/output/Taslak-Konut-Santiye-Sefi.html
```
