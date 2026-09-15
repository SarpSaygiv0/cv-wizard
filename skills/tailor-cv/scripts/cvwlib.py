"""Shared helpers for the cv-wizard scripts: workspace discovery, settings, document kinds,
and the native-library setup WeasyPrint needs on macOS. Standard library only."""

from __future__ import annotations

import os
import re
import subprocess
import sys
from dataclasses import dataclass, field
from pathlib import Path

CONFIG_NAME = "cv-wizard.toml"
SKILL_DIR = Path(__file__).resolve().parent.parent
THEMES_DIR = SKILL_DIR / "assets" / "themes"

KINDS = ("cv", "cover-letter")
PAGE_SIZES = {"a4": "A4", "letter": "Letter"}
DENSITIES = ("normal", "compact")

_SETTINGS_KEYS = {"language", "page_size", "density", "theme", "accent_color", "custom_css", "photo", "delivery"}
_DELIVERY_KEYS = {"copy_to", "cv_filename", "cover_letter_filename"}
_HEX_COLOR = re.compile(r"#(?:[0-9a-fA-F]{3}|[0-9a-fA-F]{6})")
_KIND_META = re.compile(r"<meta\b[^>]*\bname\s*=\s*[\"']cv-wizard:kind[\"'][^>]*>", re.IGNORECASE)
_CONTENT_ATTR = re.compile(r"\bcontent\s*=\s*[\"']([^\"']*)[\"']", re.IGNORECASE)


class ConfigError(Exception):
    """cv-wizard.toml can't be read or holds an invalid value."""


@dataclass
class Settings:
    workspace: Path | None = None
    language: str = "en"
    page_size: str = "A4"
    density: str = "normal"
    theme: str = "classic"
    accent_color: str | None = None
    custom_css: Path | None = None
    photo: Path | None = None
    copy_to: Path | None = None
    cv_filename: str = "CV.pdf"
    cover_letter_filename: str = "Cover_Letter.pdf"
    warnings: list[str] = field(default_factory=list)

    @property
    def theme_dir(self) -> Path:
        return THEMES_DIR / self.theme

    def delivery_filename(self, kind: str) -> str:
        return self.cv_filename if kind == "cv" else self.cover_letter_filename


def find_workspace(start: Path | None = None) -> Path | None:
    """Return the nearest folder at or above `start` holding cv-wizard.toml, else $CV_WIZARD_HOME."""
    here = Path(start or Path.cwd()).expanduser().resolve()
    if not here.is_dir():
        here = here.parent
    for folder in (here, *here.parents):
        if (folder / CONFIG_NAME).is_file():
            return folder
    home = os.environ.get("CV_WIZARD_HOME")
    if home:
        folder = Path(home).expanduser().resolve()
        if (folder / CONFIG_NAME).is_file():
            return folder
    return None


def load_settings(workspace: Path | None) -> Settings:
    """Read and validate a workspace's cv-wizard.toml. Without a workspace, return the defaults."""
    settings = Settings(workspace=workspace)
    if workspace is None:
        return settings
    try:
        import tomllib
    except ModuleNotFoundError as exc:  # Python < 3.11
        raise ConfigError("reading cv-wizard.toml needs Python 3.11 or newer") from exc

    path = workspace / CONFIG_NAME
    try:
        with path.open("rb") as handle:
            data = tomllib.load(handle)
    except OSError as exc:
        raise ConfigError(f"can't read {path}: {exc.strerror or exc}") from exc
    except tomllib.TOMLDecodeError as exc:
        raise ConfigError(f"{path} isn't valid TOML: {exc}") from exc

    delivery = data.get("delivery", {})
    if not isinstance(delivery, dict):
        raise ConfigError("[delivery] must be a table")
    settings.warnings += [f"unknown setting '{key}' in {CONFIG_NAME}" for key in data if key not in _SETTINGS_KEYS]
    settings.warnings += [
        f"unknown setting 'delivery.{key}' in {CONFIG_NAME}" for key in delivery if key not in _DELIVERY_KEYS
    ]

    settings.language = _text(data, "language", settings.language)

    page_size = _text(data, "page_size", settings.page_size)
    if page_size.lower() not in PAGE_SIZES:
        raise ConfigError(f'page_size must be "A4" or "Letter", not "{page_size}"')
    settings.page_size = PAGE_SIZES[page_size.lower()]

    settings.density = _text(data, "density", settings.density).lower()
    if settings.density not in DENSITIES:
        raise ConfigError(f'density must be "normal" or "compact", not "{settings.density}"')

    settings.theme = _text(data, "theme", settings.theme)
    if not (THEMES_DIR / settings.theme / "cv.css").is_file():
        available = ", ".join(sorted(p.name for p in THEMES_DIR.iterdir() if p.is_dir()))
        raise ConfigError(f'theme "{settings.theme}" doesn\'t exist (available: {available})')

    accent = data.get("accent_color")
    if accent is not None:
        if not isinstance(accent, str) or not _HEX_COLOR.fullmatch(accent):
            raise ConfigError(f'accent_color must be a hex color such as "#1f3a5f", not {accent!r}')
        settings.accent_color = accent

    settings.custom_css = _path(workspace, data, "custom_css")
    settings.photo = _path(workspace, data, "photo")
    settings.copy_to = _path(workspace, delivery, "copy_to", "delivery.")
    settings.cv_filename = _filename(delivery, "cv_filename", settings.cv_filename)
    settings.cover_letter_filename = _filename(delivery, "cover_letter_filename", settings.cover_letter_filename)
    return settings


def detect_kind(html: str) -> str | None:
    """Return the kind declared by <meta name="cv-wizard:kind" content="...">, if any."""
    tag = _KIND_META.search(html)
    if not tag:
        return None
    content = _CONTENT_ATTR.search(tag.group(0))
    return content.group(1).strip().lower() if content else None


def ensure_native_libs() -> None:
    """Make Homebrew's pango and glib visible to Python on macOS, re-executing once.

    Interpreters that don't come from Homebrew (python.org, pyenv, uv) don't search
    Homebrew's lib folder, so importing WeasyPrint fails. dyld reads
    DYLD_FALLBACK_LIBRARY_PATH only when a process starts, hence the re-exec.
    """
    if sys.platform != "darwin" or os.environ.get("CV_WIZARD_LIBS_READY"):
        return
    os.environ["CV_WIZARD_LIBS_READY"] = "1"
    candidates = []
    try:
        prefix = subprocess.run(["brew", "--prefix"], capture_output=True, text=True, timeout=10).stdout.strip()
        if prefix:
            candidates.append(os.path.join(prefix, "lib"))
    except (OSError, subprocess.SubprocessError):
        pass
    candidates += ["/opt/homebrew/lib", "/usr/local/lib"]
    current = [part for part in os.environ.get("DYLD_FALLBACK_LIBRARY_PATH", "").split(":") if part]
    missing = [folder for folder in dict.fromkeys(candidates) if os.path.isdir(folder) and folder not in current]
    if not missing:
        return
    # An unset DYLD_FALLBACK_LIBRARY_PATH means dyld's defaults, so keep /usr/lib when replacing it.
    os.environ["DYLD_FALLBACK_LIBRARY_PATH"] = ":".join(missing + (current or ["/usr/lib"]))
    os.execv(sys.executable, [sys.executable, *sys.argv])


def _text(table: dict, key: str, default: str, section: str = "") -> str:
    value = table.get(key, default)
    if not isinstance(value, str) or not value.strip():
        raise ConfigError(f"{section}{key} must be a non-empty string")
    return value.strip()


def _path(workspace: Path, table: dict, key: str, section: str = "") -> Path | None:
    if key not in table:
        return None
    path = Path(_text(table, key, "", section)).expanduser()
    return path if path.is_absolute() else workspace / path


def _filename(table: dict, key: str, default: str) -> str:
    name = _text(table, key, default, "delivery.")
    if Path(name).name != name:
        raise ConfigError(f"delivery.{key} must be a file name, not a path: {name!r}")
    return name
