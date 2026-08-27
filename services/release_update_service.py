"""Safe installer-based update delivery from approved LAN folders.

Discovery reads only a small catalog in a background worker.
The potentially long copy and SHA-256 verification happen only after the user
has accepted the update, never while Tkinter's event loop is running.
"""

from __future__ import annotations

import hashlib
import json
import os
import re
import shutil
import tempfile
import zipfile
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Iterable

CATALOG_NAME = "latest.json"
CONFIG_NAME = "update_sources.default.json"
MAX_CATALOG_BYTES = 256 * 1024
MAX_INSTALLER_BYTES = 1024 * 1024 * 1024
SEMVER = re.compile(r"^(0|[1-9]\d*)\.(0|[1-9]\d*)\.(0|[1-9]\d*)$")
PACKAGE_NAME = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._-]*\.mpupdate$", re.IGNORECASE)


class UpdateError(ValueError):
    pass


@dataclass(frozen=True)
class UpdateCandidate:
    version: str
    package: Path
    size: int
    sha256: str
    notes: str


def _version(value: str) -> tuple[int, int, int]:
    match = SEMVER.fullmatch(str(value))
    if not match:
        raise UpdateError(f"Invalid semantic version: {value}")
    return tuple(int(part) for part in match.groups())


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def _read_json(path: Path) -> Any:
    try:
        if path.stat().st_size > MAX_CATALOG_BYTES:
            raise UpdateError("Update catalog is too large")
        return json.loads(path.read_text(encoding="utf-8-sig"))
    except UpdateError:
        raise
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        raise UpdateError(f"Cannot read update catalog: {path}") from exc


def current_version() -> str:
    root = Path(__file__).resolve().parent.parent
    try:
        value = json.loads((root / "release.json").read_text(encoding="utf-8-sig"))
        version = str(value["version"])
        _version(version)
        return version
    except (OSError, KeyError, TypeError, json.JSONDecodeError, UpdateError):
        import config
        return str(config.APP_VERSION)


def load_sources() -> list[Path]:
    root = Path(__file__).resolve().parent.parent
    value = _read_json(root / CONFIG_NAME)
    if not isinstance(value, dict) or value.get("schema") != 1 or not isinstance(value.get("sources"), list):
        raise UpdateError("Invalid update source configuration")
    return [Path(item["location"]) for item in value["sources"] if isinstance(item, dict) and item.get("type") == "folder" and item.get("enabled") is True and isinstance(item.get("location"), str)]


def _candidate_from_catalog(folder: Path, installed_version: str) -> UpdateCandidate | None:
    value = _read_json(folder / CATALOG_NAME)
    required = {"schema", "version", "package", "sha256", "size", "notes"}
    if not isinstance(value, dict) or set(value) != required or value["schema"] != 1:
        raise UpdateError("Invalid latest.json schema")
    version = str(value["version"])
    package_name = value["package"]
    digest = value["sha256"]
    size = value["size"]
    notes = value["notes"]
    if not PACKAGE_NAME.fullmatch(str(package_name)) or not isinstance(digest, str) or not re.fullmatch(r"[0-9a-f]{64}", digest.casefold()):
        raise UpdateError("Invalid update artifact metadata")
    if not isinstance(size, int) or isinstance(size, bool) or not 0 < size <= MAX_INSTALLER_BYTES or not isinstance(notes, str) or len(notes) > 2000:
        raise UpdateError("Invalid update artifact size or notes")
    if _version(version) <= _version(installed_version):
        return None
    package = folder / str(package_name)
    # This is metadata only; do not hash an installer during startup discovery.
    if not package.is_file() or package.stat().st_size != size:
        return None
    return UpdateCandidate(version, package, size, digest.casefold(), notes)


def discover_update(installed_version: str | None = None, sources: Iterable[Path] | None = None) -> UpdateCandidate | None:
    version = installed_version or current_version()
    candidates = []
    for folder in (sources if sources is not None else load_sources()):
        try:
            candidate = _candidate_from_catalog(folder, version)
        except (OSError, UpdateError):
            continue
        if candidate is not None:
            candidates.append(candidate)
    return max(candidates, key=lambda item: _version(item.version), default=None)


def download_installer(candidate: UpdateCandidate) -> Path:
    cache = Path(os.environ.get("LOCALAPPDATA", Path.home() / "AppData" / "Local")) / "SosanhCTTTData" / "updates"
    cache.mkdir(parents=True, exist_ok=True)
    destination = cache / candidate.package.name
    descriptor, temporary_name = tempfile.mkstemp(prefix="download-", suffix=".tmp", dir=cache)
    os.close(descriptor)
    temporary = Path(temporary_name)
    copied = 0
    try:
        with candidate.package.open("rb") as source, temporary.open("wb") as target:
            for block in iter(lambda: source.read(1024 * 1024), b""):
                copied += len(block)
                if copied > MAX_INSTALLER_BYTES:
                    raise UpdateError("Installer exceeds size limit")
                target.write(block)
        if copied != candidate.size or _sha256(temporary) != candidate.sha256:
            raise UpdateError("Downloaded installer does not match latest.json")
        os.replace(temporary, destination)
        with zipfile.ZipFile(destination) as archive:
            manifest = json.loads(archive.read("manifest.json").decode("utf-8-sig"))
            files = manifest.get("files") if isinstance(manifest, dict) else None
            if (manifest.get("schema") != 1 or manifest.get("kind") != "installer"
                    or manifest.get("version") != candidate.version or not isinstance(files, list) or len(files) != 1):
                raise UpdateError("Invalid update package manifest")
            item = files[0]
            name = item.get("path") if isinstance(item, dict) else None
            if not isinstance(name, str) or not name.casefold().endswith(".exe") or name != manifest.get("installer"):
                raise UpdateError("Invalid update package installer")
            extracted = cache / name
            data = archive.read(name)
            extracted.write_bytes(data)
            if extracted.stat().st_size != item.get("size") or _sha256(extracted) != item.get("sha256"):
                extracted.unlink(missing_ok=True)
                raise UpdateError("Update package installer verification failed")
        return extracted
    except Exception:
        temporary.unlink(missing_ok=True)
        raise
