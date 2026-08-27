"""Compatibility facade for the installer-based release updater."""

from services.release_update_service import UpdateCandidate, current_version, discover_update, download_installer


def get_current_version():
    return current_version()


def check_for_update():
    candidate = discover_update()
    if candidate is None:
        return False, None, None
    return True, candidate.version, candidate


def perform_update(candidate: UpdateCandidate, callback_on_start=None):
    installer = download_installer(candidate)
    if callback_on_start:
        callback_on_start()
    import subprocess
    subprocess.Popen([str(installer), "/SP-", "/CLOSEAPPLICATIONS", "/RESTARTAPPLICATIONS"], close_fds=True)
    return True
