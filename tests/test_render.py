"""Tests for the cv-wizard scripts and packaging.

Run from the repository root:

    python3 -m unittest discover -s tests -v

Rendering tests run the scripts in subprocesses, the same way the skills do, so they need
WeasyPrint (see README).
"""

from __future__ import annotations

import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

ROOT = Path(__file__).resolve().parent.parent
SKILLS = ROOT / "skills"
ASSETS = SKILLS / "tailor-cv" / "assets"
SCRIPTS = SKILLS / "tailor-cv" / "scripts"
RENDER = SCRIPTS / "render.py"
DOCTOR = SCRIPTS / "doctor.py"
EXAMPLES = ROOT / "examples"

sys.path.insert(0, str(SCRIPTS))
import cvwlib  # noqa: E402

RENDERED = re.compile(
    r"^OK +rendered (?P<kind>\S+) -> (?P<pdf>.+) \((?P<pages>\d+) pages?, (?P<width>\d+)x(?P<height>\d+) mm\)$",
    re.MULTILINE,
)
PAGE_MM = {"A4": (210, 297), "Letter": (216, 279)}
AGENT_SKILLS_FIELDS = {"name", "description", "license", "compatibility", "metadata", "allowed-tools"}


def run_script(script: Path, *args, cwd: Path | str | None = None) -> subprocess.CompletedProcess:
    env = {key: value for key, value in os.environ.items() if key != "CV_WIZARD_HOME"}
    return subprocess.run(
        [sys.executable, str(script), *map(str, args)],
        cwd=cwd, env=env, capture_output=True, text=True, timeout=180,
    )


def render(html: Path, *args) -> tuple[subprocess.CompletedProcess, re.Match | None]:
    result = run_script(RENDER, html, *args)
    return result, RENDERED.search(result.stdout)


def frontmatter(text: str) -> dict[str, str]:
    lines = text.splitlines()
    if not lines or lines[0] != "---":
        raise AssertionError("SKILL.md must start with YAML frontmatter")
    fields = {}
    for line in lines[1:lines.index("---", 1)]:
        if line and not line[0].isspace():
            key, _, value = line.partition(":")
            fields[key.strip()] = value.strip()
    return fields


class ExampleDocumentsTest(unittest.TestCase):
    def test_every_example_document_renders_on_one_page(self):
        documents = sorted(EXAMPLES.glob("*/output/*.html"))
        self.assertGreaterEqual(len(documents), 4)
        with tempfile.TemporaryDirectory() as tmp:
            for html in documents:
                with self.subTest(document=str(html.relative_to(ROOT))):
                    settings = cvwlib.load_settings(cvwlib.find_workspace(html))
                    pdf = Path(tmp) / f"{html.parent.parent.name}-{html.stem}.pdf"
                    result, match = render(html, "--out", pdf, "--no-copy")
                    output = result.stdout + result.stderr
                    self.assertEqual(result.returncode, 0, output)
                    self.assertIsNotNone(match, output)
                    self.assertNotIn("WARN", result.stdout)
                    self.assertEqual(match["pages"], "1", output)
                    self.assertEqual(match["kind"], cvwlib.detect_kind(html.read_text(encoding="utf-8")))
                    self.assertEqual((int(match["width"]), int(match["height"])), PAGE_MM[settings.page_size])
                    self.assertTrue(pdf.is_file())

    def test_each_example_has_a_cv_and_a_cover_letter(self):
        for workspace in sorted(path.parent for path in EXAMPLES.glob("*/cv-wizard.toml")):
            with self.subTest(workspace=workspace.name):
                kinds = {cvwlib.detect_kind(p.read_text(encoding="utf-8")) for p in (workspace / "output").glob("*.html")}
                self.assertEqual(kinds, {"cv", "cover-letter"})

    @unittest.skipUnless(shutil.which("pdftotext"), "pdftotext not installed")
    def test_pdf_text_is_extractable(self):
        cases = [
            (EXAMPLES / "jordan-avery" / "output" / "Hooli-Backend-Engineer.html", ["Globex Logistics", "Kafka"]),
            (EXAMPLES / "deniz-yilmaz" / "output" / "Taslak-Konut-Santiye-Sefi.html", ["Örnek Yapı", "hakediş"]),
        ]
        with tempfile.TemporaryDirectory() as tmp:
            for html, phrases in cases:
                with self.subTest(document=html.name):
                    pdf = Path(tmp) / f"{html.stem}.pdf"
                    result, _ = render(html, "--out", pdf, "--no-copy")
                    self.assertEqual(result.returncode, 0, result.stderr)
                    text = subprocess.run(["pdftotext", str(pdf), "-"], capture_output=True, text=True).stdout
                    for phrase in phrases:
                        self.assertIn(phrase, text)


class TemplatesTest(unittest.TestCase):
    def test_templates_render(self):
        with tempfile.TemporaryDirectory() as tmp:
            for name, kind, max_pages in (("cv-template.html", "cv", 2), ("cover-letter-template.html", "cover-letter", 1)):
                with self.subTest(template=name):
                    result, match = render(ASSETS / name, "--out", Path(tmp) / f"{kind}.pdf", "--no-copy")
                    self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
                    self.assertIsNotNone(match, result.stdout)
                    self.assertEqual(match["kind"], kind)
                    self.assertLessEqual(int(match["pages"]), max_pages)


class DeliveryTest(unittest.TestCase):
    def test_copies_by_declared_kind_not_filename(self):
        with tempfile.TemporaryDirectory() as tmp:
            workspace, inbox = Path(tmp) / "workspace", Path(tmp) / "inbox"
            inbox.mkdir()
            shutil.copytree(EXAMPLES / "deniz-yilmaz", workspace)
            config = workspace / cvwlib.CONFIG_NAME
            settings_part = config.read_text(encoding="utf-8").split("[delivery]")[0]
            config.write_text(
                settings_part + f'[delivery]\ncopy_to = "{inbox.as_posix()}"\n'
                'cv_filename = "CV.pdf"\ncover_letter_filename = "Letter.pdf"\n',
                encoding="utf-8",
            )
            for html in sorted((workspace / "output").glob("*.html")):
                result, _ = render(html)
                self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
                self.assertIn("copied ->", result.stdout)
            self.assertEqual(sorted(p.name for p in inbox.iterdir()), ["CV.pdf", "Letter.pdf"])

            (inbox / "CV.pdf").unlink()
            result, _ = render(workspace / "output" / "Taslak-Konut-Santiye-Sefi.html", "--no-copy")
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertFalse((inbox / "CV.pdf").exists())


class SettingsTest(unittest.TestCase):
    def workspace_with(self, text: str) -> Path:
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        workspace = Path(tmp.name)
        (workspace / cvwlib.CONFIG_NAME).write_text(text, encoding="utf-8")
        return workspace

    def test_defaults_without_a_workspace(self):
        settings = cvwlib.load_settings(None)
        self.assertEqual((settings.page_size, settings.density, settings.theme), ("A4", "normal", "classic"))

    def test_values_are_normalized_and_paths_resolved(self):
        workspace = self.workspace_with(
            'page_size = "letter"\ndensity = "Compact"\naccent_color = "#123abc"\nphoto = "me.jpg"\n'
            '[delivery]\ncopy_to = "inbox"\ncv_filename = "Me_CV.pdf"\n'
        )
        settings = cvwlib.load_settings(workspace)
        self.assertEqual(settings.page_size, "Letter")
        self.assertEqual(settings.density, "compact")
        self.assertEqual(settings.photo, workspace / "me.jpg")
        self.assertEqual(settings.copy_to, workspace / "inbox")
        self.assertEqual(settings.delivery_filename("cv"), "Me_CV.pdf")
        self.assertEqual(settings.delivery_filename("cover-letter"), "Cover_Letter.pdf")

    def test_invalid_values_are_rejected(self):
        for text in (
            'page_size = "A5"\n',
            'density = "tight"\n',
            'accent_color = "red"\n',
            'theme = "no-such-theme"\n',
            "language = 5\n",
            "page_size =\n",
            '[delivery]\ncv_filename = "../CV.pdf"\n',
        ):
            with self.subTest(config=text):
                with self.assertRaises(cvwlib.ConfigError):
                    cvwlib.load_settings(self.workspace_with(text))

    def test_unknown_keys_produce_warnings(self):
        settings = cvwlib.load_settings(self.workspace_with('pagesize = "A4"\n[delivery]\ncopyto = "x"\n'))
        self.assertEqual(len(settings.warnings), 2)


class WorkspaceDiscoveryTest(unittest.TestCase):
    def test_walks_up_from_a_file_inside_the_workspace(self):
        html = EXAMPLES / "jordan-avery" / "output" / "Hooli-Backend-Engineer.html"
        self.assertEqual(cvwlib.find_workspace(html), (EXAMPLES / "jordan-avery").resolve())

    def test_falls_back_to_cv_wizard_home(self):
        home = str(EXAMPLES / "deniz-yilmaz")
        with tempfile.TemporaryDirectory() as tmp, mock.patch.dict(os.environ, {"CV_WIZARD_HOME": home}):
            self.assertEqual(cvwlib.find_workspace(Path(tmp)), (EXAMPLES / "deniz-yilmaz").resolve())

    def test_returns_none_when_nothing_is_found(self):
        with tempfile.TemporaryDirectory() as tmp, mock.patch.dict(os.environ, {"CV_WIZARD_HOME": ""}):
            self.assertIsNone(cvwlib.find_workspace(Path(tmp)))

    def test_reads_the_declared_kind_in_any_attribute_order(self):
        self.assertEqual(cvwlib.detect_kind('<meta name="cv-wizard:kind" content="cover-letter">'), "cover-letter")
        self.assertEqual(cvwlib.detect_kind("<meta content='CV' name='cv-wizard:kind' />"), "cv")
        self.assertIsNone(cvwlib.detect_kind('<meta charset="utf-8">'))


class DoctorTest(unittest.TestCase):
    def test_brief_reports_the_workspace(self):
        result = run_script(DOCTOR, "--brief", cwd=EXAMPLES / "jordan-avery" / "output")
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn(f"workspace: {(EXAMPLES / 'jordan-avery').resolve()}", result.stdout)

    def test_brief_without_a_workspace_exits_2(self):
        with tempfile.TemporaryDirectory() as tmp:
            result = run_script(DOCTOR, "--brief", cwd=tmp)
        self.assertEqual(result.returncode, 2, result.stdout + result.stderr)

    def test_full_check_passes_for_an_example(self):
        result = run_script(DOCTOR, "--workspace", EXAMPLES / "deniz-yilmaz")
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn("OK    test render", result.stdout)


class PackagingTest(unittest.TestCase):
    def test_skills_use_only_portable_frontmatter(self):
        skills = sorted(SKILLS.glob("*/SKILL.md"))
        self.assertEqual([path.parent.name for path in skills], ["setup", "tailor-cv"])
        for skill in skills:
            with self.subTest(skill=skill.parent.name):
                text = skill.read_text(encoding="utf-8")
                fields = frontmatter(text)
                self.assertLessEqual(set(fields), AGENT_SKILLS_FIELDS)
                self.assertEqual(fields["name"], skill.parent.name)
                self.assertRegex(fields["name"], r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
                self.assertTrue(0 < len(fields["description"]) <= 1024)
                self.assertLessEqual(len(fields.get("compatibility", "")), 500)
                self.assertLess(text.count("\n"), 500)

    def test_plugin_and_marketplace_manifests_agree(self):
        plugin = json.loads((ROOT / ".claude-plugin" / "plugin.json").read_text(encoding="utf-8"))
        marketplace = json.loads((ROOT / ".claude-plugin" / "marketplace.json").read_text(encoding="utf-8"))
        self.assertEqual([entry["name"] for entry in marketplace["plugins"]], [plugin["name"]])


if __name__ == "__main__":
    unittest.main()
