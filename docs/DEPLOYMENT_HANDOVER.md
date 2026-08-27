# Deployment Handover: Inno Setup 6 And LAN Updates

## Release Locations

Installer files are published to:

`\\fstvn01\Data\10_Production Engineering Department(製造技術部)\02.製造技術課\PE Dept\15. FORM（BIEU MAU）-形式\Form_VBA\Form_Phanmem_sosanhCTTT`

The automatic-update catalog and matching `.mpupdate` package are published to:

`\\fstvn01\Data\10_Production Engineering Department(製造技術部)\02.製造技術課\PE Dept\15. FORM（BIEU MAU）-形式\Form_VBA\Form_Phanmem_sosanhCTTT\release_update`

## Cross-Project Lesson: UNC Timing

This is a shared lesson from `PM_in_lai_phieuhienvat` and `SosanhCTTT`.

Do not apply a short fixed timeout to an SMB/UNC update probe. A share can need
several seconds to establish a connection even when it is healthy. The prior
two-second probe timeout returned `no update` before `latest.json` arrived,
which creates a false negative and hides a real release.

The correct rule is:

1. Never perform UNC I/O from the Tkinter event thread.
2. Run the complete catalog probe in a daemon worker and let it wait for the
   network result. A disconnected share may leave that worker waiting, but it
   must not freeze or block the UI.
3. Do not enumerate or hash a large installer during discovery. Read only the
   small `latest.json` catalog.
4. Download, size-check, and SHA-256 verify the installer only after the user
   explicitly accepts the update. These operations also run in a worker.

`services/release_update_service.py` and
`ui/main_window_modern.py` implement this rule. Do not reintroduce `Event.wait`
or a hard deadline around catalog discovery unless operations explicitly accept
the risk of missing slow but valid update shares.

## Design

- `release.json` is the release version source. Use `major.minor.patch`.
- `installer/SosanhCTTT.iss` installs the PyInstaller `onedir` bundle to
  `%LOCALAPPDATA%\SosanhCTTT` with a stable Inno `AppId`, so a later setup is an
  upgrade rather than a second application.
- `services/settings_service.py` writes mutable user settings to
  `%LOCALAPPDATA%\SosanhCTTTData`; installer upgrades do not overwrite them.
- `services/release_update_service.py` validates the catalog, downloads the
  `.mpupdate`, checks its SHA-256, validates `manifest.json`, and extracts only
  the verified installer to the local cache before starting it.
- The update remains user-confirmed. It is an automatic notification plus a
  manual acceptance/install flow, not a silent replacement of a running `.exe`.

## Build And Publish

1. Change the version in both `release.json` and
   `installer/SosanhCTTT.iss`.
2. Run `py run_tests.py`.
3. Run `py package_app.py` to create
   `release_artifacts\SosanhCTTT_Setup_<version>.exe` locally. It requires
   PyInstaller and Inno Setup 6 (`ISCC.exe`).
4. Run `py package_app.py --publish` to copy the verified installer to the
   release folder.
5. Run `py package_app.py --publish-update --release-notes "Description"` to
   create and copy `SosanhCTTT-<version>.mpupdate` to `release_update`, then
   atomically publish `latest.json` last. Never rename a raw `.exe` to `.mpupdate`.

The publish sequence copies to a `.part` file, checks SHA-256, then uses
`os.replace`. `latest.json` is written only after the installer is complete, so
clients never receive a catalog for a partial file.

## `.mpupdate` Contract And Bootstrap Migration

A `.mpupdate` is a ZIP package, never a renamed executable. It must contain:

```text
manifest.json
SosanhCTTT_Setup_<version>.exe
```

`manifest.json` must declare `schema: 1`, `kind: "installer"`, the matching
semantic version, installer file name, and an inventory entry with exact size
and SHA-256. The client verifies the catalog hash first, then validates the
package manifest and installer hash before it starts the installer.

The installer remains the bootstrap trust boundary for machines on an older
release. A build that predates `.mpupdate` support cannot consume a package;
publish its matching Setup in the main release folder and upgrade it once.
After that bootstrap version is installed, publish future releases as
`.mpupdate` packages in `release_update` and publish `latest.json` last.

Do not overwrite an already published catalog with a `.mpupdate` version that
older installed clients cannot parse. Use a documented bootstrap Setup release
first, then move the update channel to `.mpupdate`.

## Catalog Format

```json
{
  "schema": 1,
  "version": "7.5.0",
  "package": "SosanhCTTT-7.5.0.mpupdate",
  "sha256": "64 lowercase hexadecimal characters",
  "size": 12345678,
  "notes": "Brief release note"
}
```

The release share ACL is the trust boundary. Only authorized release owners
should have write permission. SHA-256 verifies delivery integrity but is not a
substitute for ACLs or Authenticode signing.

## Required Release Checks

- Fresh install and upgrade over an existing version.
- Manual `Check for updates` from the Help menu.
- A slow but reachable share: it must still detect the catalog after its SMB
  connection completes.
- A disconnected share: the GUI must remain usable.
- A deliberately modified installer or incorrect catalog hash: installation
  must not launch.
