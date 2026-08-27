"""Build a PyInstaller onedir bundle, compile Inno Setup, and publish safely."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
ARTIFACTS = ROOT / "release_artifacts"
BUNDLE = ARTIFACTS / "install_bundle"
PUBLISH_DIR = Path(r"\\fstvn01\Data\10_Production Engineering Department(\u88fd\u9020\u6280\u8853\u90e8)\02.\u88fd\u9020\u6280\u8853\u8ab2\PE Dept\15. FORM\uff08BIEU MAU\uff09-\u5f62\u5f0f\Form_VBA\Form_Phanmem_sosanhCTTT")
UPDATE_DIR = PUBLISH_DIR / "release_update"

# Use a Windows UNC path with forward separators so the non-ASCII share names
# remain readable and are not accidentally treated as literal ``\\uXXXX`` text.
PUBLISH_DIR = Path("//fstvn01/Data/10_Production Engineering Department(製造技術部)/02.製造技術課/PE Dept/15. FORM（BIEU MAU）-形式/Form_VBA/Form_Phanmem_sosanhCTTT")
UPDATE_DIR = PUBLISH_DIR / "release_update"


def release() -> dict:
    value = json.loads((ROOT / "release.json").read_text(encoding="utf-8-sig"))
    if not isinstance(value.get("version"), str):
        raise ValueError("release.json must contain a version")
    return value


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def find_iscc() -> Path | None:
    found = shutil.which("ISCC") or shutil.which("iscc")
    if found:
        return Path(found)
    for raw in (r"%LOCALAPPDATA%\Programs\Inno Setup 6\ISCC.exe", r"%ProgramFiles(x86)%\Inno Setup 6\ISCC.exe", r"%ProgramFiles%\Inno Setup 6\ISCC.exe"):
        candidate = Path(os.path.expandvars(raw))
        if candidate.is_file():
            return candidate
    return None


def build_bundle() -> Path:
    subprocess.run([
        sys.executable, "-m", "PyInstaller", "--noconfirm", "--clean", "--onedir", "--windowed",
        "--name", "SosanhCTTT", "--distpath", str(ROOT / "dist"), "--workpath", str(ROOT / "build"),
        "--specpath", str(ROOT / "build" / "specs"), "--add-data", f"{ROOT / 'assets'}{os.pathsep}assets",
        "--add-data", f"{ROOT / 'release.json'}{os.pathsep}.", "--add-data", f"{ROOT / 'update_sources.default.json'}{os.pathsep}.",
        "--hidden-import", "pythoncom", "--hidden-import", "pywintypes", "--hidden-import", "win32com.client", str(ROOT / "main.py")
    ], check=True, cwd=ROOT)
    source = ROOT / "dist" / "SosanhCTTT"
    if not (source / "SosanhCTTT.exe").is_file():
        raise RuntimeError("PyInstaller did not create SosanhCTTT.exe")
    if BUNDLE.exists():
        shutil.rmtree(BUNDLE)
    shutil.copytree(source, BUNDLE)
    return BUNDLE


def compile_installer() -> Path:
    compiler = find_iscc()
    if compiler is None:
        raise FileNotFoundError("Install Inno Setup 6 so ISCC.exe is available")
    subprocess.run([str(compiler), str(ROOT / "installer" / "SosanhCTTT.iss")], check=True, cwd=ROOT)
    artifact = ARTIFACTS / f"SosanhCTTT_Setup_{release()['version']}.exe"
    if not artifact.is_file():
        raise RuntimeError("Inno Setup did not create the expected installer")
    return artifact


def publish_installer(installer: Path, destination: Path = PUBLISH_DIR) -> Path:
    destination.mkdir(parents=True, exist_ok=True)
    partial = destination / f"{installer.name}.part"
    final = destination / installer.name
    shutil.copyfile(installer, partial)
    if sha256(installer) != sha256(partial):
        partial.unlink(missing_ok=True)
        raise RuntimeError("Installer hash changed during publish")
    os.replace(partial, final)
    return final


def publish_catalog(installer: Path, notes: str, destination: Path = UPDATE_DIR) -> Path:
    destination.mkdir(parents=True, exist_ok=True)
    published = publish_installer(installer, destination)
    catalog = {"schema": 1, "version": release()["version"], "installer": published.name, "sha256": sha256(published), "size": published.stat().st_size, "notes": notes}
    partial = destination / "latest.json.part"
    partial.write_text(json.dumps(catalog, ensure_ascii=True, indent=2) + "\n", encoding="utf-8")
    os.replace(partial, destination / "latest.json")
    return published


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--publish", action="store_true", help="Copy the completed setup exe to the release share")
    parser.add_argument("--publish-update", action="store_true", help="Publish the setup exe and latest.json to release_update")
    parser.add_argument("--release-notes", default="")
    args = parser.parse_args()
    build_bundle()
    installer = compile_installer()
    if args.publish:
        print(publish_installer(installer))
    if args.publish_update:
        print(publish_catalog(installer, args.release_notes))
    print(installer)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
