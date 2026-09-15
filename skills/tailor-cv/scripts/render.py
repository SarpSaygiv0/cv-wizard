#!/usr/bin/env python3
"""Render a cv-wizard HTML document (a CV or a cover letter) to PDF.

    python3 render.py output/Acme-Backend-Engineer.html
    python3 render.py output/Acme-Cover-Letter.html --no-copy

Settings come from the workspace's cv-wizard.toml, found by walking up from the HTML file
(or given with --workspace): theme, page size, density, accent color, custom CSS, and
delivery. The document kind comes from <meta name="cv-wizard:kind" content="..."> in the
HTML, or --kind. Output lines start with OK, WARN, or ERROR.
"""

from __future__ import annotations

import argparse
import logging
import shutil
import sys
from pathlib import Path

import cvwlib

PAGE_TARGET = 1  # CVs and cover letters both aim for one page


class _Collector(logging.Handler):
    """Collects WeasyPrint's log messages so they can be reported after rendering."""

    def __init__(self) -> None:
        super().__init__(logging.WARNING)
        self.messages: list[str] = []

    def emit(self, record: logging.LogRecord) -> None:
        self.messages.append(record.getMessage())


def stylesheets(settings: cvwlib.Settings, kind: str, css, font_config) -> list:
    """The theme sheet, density overrides, page size and accent color, then the workspace's CSS."""
    theme = settings.theme_dir
    sheets = [css(filename=str(theme / f"{kind}.css"), font_config=font_config)]
    compact = theme / f"{kind}-compact.css"
    if settings.density == "compact" and compact.is_file():
        sheets.append(css(filename=str(compact), font_config=font_config))
    overrides = f"@page {{ size: {settings.page_size}; }}"
    if settings.accent_color:
        overrides += f"\n:root {{ --accent: {settings.accent_color}; }}"
    sheets.append(css(string=overrides, font_config=font_config))
    if settings.custom_css:
        sheets.append(css(filename=str(settings.custom_css), font_config=font_config))
    return sheets


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Render a cv-wizard HTML document to PDF.")
    parser.add_argument("html", type=Path, help="the .html file to render")
    parser.add_argument("-o", "--out", type=Path, help="where to write the PDF (default: next to the HTML)")
    parser.add_argument("--kind", choices=cvwlib.KINDS, help="document kind (default: read from the HTML, else cv)")
    parser.add_argument("--workspace", type=Path, help="workspace folder (default: found from the HTML file)")
    parser.add_argument("--no-copy", action="store_true", help="don't copy the PDF to the delivery folder")
    parser.add_argument("--verbose", action="store_true", help="also show WeasyPrint's notes about unsupported CSS")
    args = parser.parse_args(argv)
    cvwlib.ensure_native_libs()

    html_path = args.html.expanduser().resolve()
    if not html_path.is_file():
        return _error(f"input not found: {html_path}")

    try:
        workspace = args.workspace.expanduser().resolve() if args.workspace else cvwlib.find_workspace(html_path)
        settings = cvwlib.load_settings(workspace)
    except cvwlib.ConfigError as exc:
        return _error(str(exc))
    for warning in settings.warnings:
        print(f"WARN  {warning}")
    if settings.custom_css and not settings.custom_css.is_file():
        return _error(f"custom_css not found: {settings.custom_css}")

    kind = args.kind or cvwlib.detect_kind(html_path.read_text(encoding="utf-8", errors="replace")) or "cv"
    if kind not in cvwlib.KINDS:
        return _error(f'unknown document kind "{kind}" in {html_path.name} (expected "cv" or "cover-letter")')

    try:
        from weasyprint import CSS, HTML
        from weasyprint.text.fonts import FontConfiguration
    except (ImportError, OSError) as exc:
        return _error(f"WeasyPrint isn't usable ({exc}). Run doctor.py for install help.")

    pdf_path = args.out.expanduser().resolve() if args.out else html_path.with_suffix(".pdf")
    collector = _Collector()
    logger = logging.getLogger("weasyprint")
    logger.addHandler(collector)
    try:
        font_config = FontConfiguration()
        document = HTML(filename=str(html_path)).render(
            stylesheets=stylesheets(settings, kind, CSS, font_config), font_config=font_config
        )
        pdf_path.parent.mkdir(parents=True, exist_ok=True)
        document.write_pdf(pdf_path)
    except Exception as exc:  # WeasyPrint and its CSS parser raise many exception types
        return _error(f"rendering failed: {exc}")
    finally:
        logger.removeHandler(collector)

    for message in collector.messages:
        if args.verbose or not message.startswith("Ignored"):
            print(f"WARN  {message}")

    pages = len(document.pages)
    first = document.pages[0]
    size = f"{round(first.width * 25.4 / 96)}x{round(first.height * 25.4 / 96)} mm"
    print(f"OK    rendered {kind} -> {pdf_path} ({pages} page{'' if pages == 1 else 's'}, {size})")
    if pages > PAGE_TARGET:
        print(f"WARN  the {kind} runs to {pages} pages; the target is {PAGE_TARGET}")

    if settings.copy_to and not args.no_copy:
        destination = settings.copy_to / settings.delivery_filename(kind)
        if not settings.copy_to.is_dir():
            print(f"WARN  delivery folder not found, so the PDF wasn't copied: {settings.copy_to}")
        else:
            try:
                shutil.copyfile(pdf_path, destination)
            except OSError as exc:
                print(f"WARN  couldn't copy the PDF to {destination}: {exc}")
            else:
                print(f"OK    copied -> {destination}")
    return 0


def _error(message: str) -> int:
    print(f"ERROR {message}", file=sys.stderr)
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
