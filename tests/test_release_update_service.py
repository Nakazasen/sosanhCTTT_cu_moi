import hashlib
import json
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from services.release_update_service import UpdateCandidate, UpdateError, _candidate_from_catalog, download_installer


class ReleaseUpdateServiceTests(unittest.TestCase):
    def test_catalog_discovers_only_newer_matching_installer(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            package = root / "SosanhCTTT-7.5.0.mpupdate"
            package.write_bytes(b"package")
            root.joinpath("latest.json").write_text(json.dumps({
                "schema": 1, "version": "7.5.0", "package": package.name,
                "sha256": hashlib.sha256(b"package").hexdigest(), "size": package.stat().st_size, "notes": "Fixes"
            }), encoding="utf-8")
            candidate = _candidate_from_catalog(root, "7.4.0")
            self.assertEqual(candidate.version, "7.5.0")
            self.assertIsNone(_candidate_from_catalog(root, "7.5.0"))

    def test_download_rejects_hash_mismatch(self):
        with tempfile.TemporaryDirectory() as temporary:
            path = Path(temporary) / "SosanhCTTT-7.5.0.mpupdate"
            path.write_bytes(b"package")
            candidate = UpdateCandidate("7.5.0", path, path.stat().st_size, "0" * 64, "")
            with self.assertRaises(UpdateError):
                download_installer(candidate)
