#!/usr/bin/env python3
"""Check that cv-wizard can run: the workspace and its settings, Python, and WeasyPrint.

    python3 doctor.py                  full check, including a test render
    python3 doctor.py --brief          workspace and settings only (fast)
    python3 doctor.py --workspace DIR  check a specific workspace

Exit codes: 0 all good, 1 something needs fixing, 2 no workspace found (with --brief).
"""

from __future__ import annotations

import argparse
import os
import platform
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

import cvwlib

RENDER = Path(__file__).resolve().parent / "render.py"
WEASYPRINT_DOCS = "https://doc.courtbouillon.org/weasyprint/stable/first_steps.html"
INSTALL_HINTS = {
    "darwin": [
        "brew install pango",
        "python3 -m pip install weasyprint   (use a virtual environment if pip refuses a Homebrew-managed Python)",
    ],
    "linux": [
        "sudo apt install -y libpango-1.0-0 libpangoft2-1.0-0   (Debian/Ubuntu; other distros: see the WeasyPrint docs)",
        "python3 -m pip install weasyprint   (use a virtual environment if pip refuses a system-managed Python)",
    ],
}
TEST_DOCUMENT = """<!DOCTYPE html>
<html lang="en"><head><meta charset="utf-8" /><meta name="cv-wizard:kind" content="cv" />
<title>doctor</title></head><body>
<header><h1 class="name">Test Render</h1><p class="headline">cv-wizard doctor</p></header>
<section><h2 class="section">Summary</h2><p class="summary">If this PDF exists, rendering works.</p></section>
</body></html>
"""


def say(level: str, message: str) -> None:
    print(f"{level:<5} {message}")


def check_workspace(explicit: Path | None) -> tuple[int, cvwlib.Settings | None]:
    """Report on the workspace. Returns (problem count, settings or None when there's no usable workspace)."""
    if explicit is not None:
        workspace = explicit.expanduser().resolve()
        if not (workspace / cvwlib.CONFIG_NAME).is_file():
            say("FAIL", f"{workspace} has no {cvwlib.CONFIG_NAME}")
            return 1, None
    else:
        workspace = cvwlib.find_workspace(Path.cwd())
        if workspace is None:
            home = os.environ.get("CV_WIZARD_HOME")
            if home:
                say("FAIL", f"CV_WIZARD_HOME is {home}, but that folder has no {cvwlib.CONFIG_NAME}")
                return 1, None
            say("INFO", f"no workspace: no {cvwlib.CONFIG_NAME} in {Path.cwd()} or its parents, and "
                "CV_WIZARD_HOME isn't set. The setup skill creates one.")
            return 0, None

    say("OK", f"workspace: {workspace}")
    try:
        settings = cvwlib.load_settings(workspace)
    except cvwlib.ConfigError as exc:
        say("FAIL", str(exc))
        return 1, None
    for warning in settings.warnings:
        say("WARN", warning)
    say("OK", f"settings: language {settings.language}, page {settings.page_size}, "
        f"density {settings.density}, theme {settings.theme}")

    problems = 0
    for name, need in (("master-cv.md", "required"), ("preferences.md", "recommended"),
                       ("archetypes.md", "optional"), ("bullet-library.md", "optional")):
        if (workspace / name).is_file():
            say("OK", name)
        elif need == "required":
            say("FAIL", f"{name} is missing; tailoring needs it")
            problems += 1
        elif need == "recommended":
            say("WARN", f"{name} is missing; runs will use the skill's defaults")
        else:
            say("INFO", f"{name}: not present (optional)")

    for label, path in (("photo", settings.photo), ("custom_css", settings.custom_css)):
        if path is None:
            continue
        if path.is_file():
            say("OK", f"{label}: {path}")
        else:
            say("FAIL", f"{label} not found: {path}")
            problems += 1

    if settings.copy_to is None:
        say("INFO", "delivery: PDFs stay in output/")
    elif settings.copy_to.is_dir():
        say("OK", f"delivery: copies to {settings.copy_to} as "
            f"{settings.cv_filename} and {settings.cover_letter_filename}")
    else:
        say("WARN", f"delivery folder not found: {settings.copy_to}")
    return problems, settings


def check_environment(settings: cvwlib.Settings | None) -> int:
    """Report on Python, WeasyPrint, a test render, and optional tools. Returns the problem count."""
    if sys.version_info < (3, 11):
        say("FAIL", f"Python {platform.python_version()} ({sys.executable}); cv-wizard needs 3.11 or newer")
        return 1
    say("OK", f"Python {platform.python_version()} ({sys.executable})")

    try:
        import weasyprint
    except (ImportError, OSError) as exc:
        reason = str(exc).strip().splitlines()[0] if str(exc).strip() else type(exc).__name__
        say("FAIL", f"WeasyPrint can't be imported: {reason}")
        for hint in INSTALL_HINTS.get(sys.platform, []):
            say("HINT", hint)
        say("HINT", f"details: {WEASYPRINT_DOCS}")
        return 1
    say("OK", f"WeasyPrint {weasyprint.__version__}")

    problems = 0
    with tempfile.TemporaryDirectory() as tmp:
        html = Path(tmp) / "doctor.html"
        html.write_text(TEST_DOCUMENT, encoding="utf-8")
        command = [sys.executable, str(RENDER), str(html), "--no-copy"]
        if settings is not None and settings.workspace is not None:
            command += ["--workspace", str(settings.workspace)]
        result = subprocess.run(command, capture_output=True, text=True, timeout=120)
        if result.returncode == 0 and html.with_suffix(".pdf").is_file():
            say("OK", "test render")
        else:
            say("FAIL", "test render failed:")
            for line in (result.stdout + result.stderr).strip().splitlines()[-8:]:
                print(f"      {line}")
            problems += 1

    if shutil.which("pdftoppm"):
        say("OK", "pdftoppm, for page previews")
    else:
        say("INFO", "pdftoppm not found; optional, for page previews (install poppler)")
    return problems


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Check that cv-wizard can run here.")
    parser.add_argument("--workspace", type=Path, help="workspace to check (default: found from the current folder)")
    parser.add_argument("--brief", action="store_true", help="check only the workspace and its settings")
    args = parser.parse_args(argv)
    if not args.brief:
        cvwlib.ensure_native_libs()

    problems, settings = check_workspace(args.workspace)
    if args.brief:
        if problems:
            return 1
        return 0 if settings is not None else 2
    problems += check_environment(settings)
    return 1 if problems else 0


if __name__ == "__main__":
    raise SystemExit(main())
