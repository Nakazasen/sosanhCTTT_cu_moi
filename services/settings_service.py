import json
import os
import sys
import config
import utils

class SettingsService:
    def __init__(self):
        self.settings_file = self._get_settings_path()
        self.settings = self.load_settings()

    def _get_settings_path(self):
        """Determines the correct path for the settings file (EXE vs Script)."""
        if getattr(sys, 'frozen', False):
            # Installer files are replaceable; user state must survive an upgrade.
            app_dir = os.path.join(os.environ.get("LOCALAPPDATA", os.path.expanduser("~")), "SosanhCTTTData")
            os.makedirs(app_dir, exist_ok=True)
        else:
            # Running as Script
            # Go up one level from 'services' to root 'Refactored'
            app_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

        return os.path.join(app_dir, "user_settings.json")

    def load_settings(self):
        """Loads settings from JSON file or returns defaults."""
        default_settings = {
            # PDF Settings
            config.KEY_DPI: config.DEFAULT_DPI,
            config.KEY_ZOOM: config.DEFAULT_ZOOM,
            config.KEY_DIFF_THRESHOLD: config.DEFAULT_DIFF_THRESHOLD,
            config.KEY_GOTO_ADDRESS: config.DEFAULT_GOTO_ADDRESS,

            # Highlight Colors (Critical - from Gap Analysis)
            "highlight_base_color": config.HIGHLIGHT_BASE_COLOR,
            "highlight_outline_color": config.HIGHLIGHT_OUTLINE_COLOR,
            "highlight_fill_color": config.HIGHLIGHT_FILL_COLOR,

            # Highlight Settings (Critical - from Gap Analysis)
            "highlight_fill_opacity": config.DEFAULT_FILL_OPACITY,
            "pdf_diff_threshold": config.DEFAULT_DIFF_THRESHOLD,
            "pdf_dilate_size": config.DEFAULT_DILATE_SIZE,
            "pdf_dilate_iterations": config.DEFAULT_DILATE_ITERATIONS,

            # Boolean Settings
            "auto_add_b": False,
            "suppress_error": True,
            "use_pdf_method": True,
            "save_settings": True,

            # Other Settings
            "screen_mode": "pc",
            "goto_address": config.DEFAULT_GOTO_ADDRESS,
            "doc_mode": config.DOC_MODE_STANDARD_CTTT,
            "print_area": config.PRINT_AREA_STANDARD_CTTT
        }

        if os.path.exists(self.settings_file):
            try:
                with open(self.settings_file, 'r', encoding='utf-8') as f:
                    loaded = json.load(f)
                    # Merge with defaults to ensure all keys exist
                    default_settings.update(loaded)
                    utils.logger.info("Settings loaded successfully.")
            except Exception as e:
                utils.logger.error(f"Failed to load settings: {e}")

        return default_settings

    def save_settings(self, current_settings):
        """Saves current settings to JSON if 'save_settings' is True."""
        self.settings.update(current_settings)

        if self.settings.get("save_settings", True):
            try:
                with open(self.settings_file, 'w', encoding='utf-8') as f:
                    json.dump(self.settings, f, indent=4)
                utils.logger.info(f"Settings saved to {self.settings_file}")
            except Exception as e:
                utils.logger.error(f"Failed to save settings: {e}")
        else:
            utils.logger.info("Settings save skipped (disabled by user).")

    def get(self, key, default=None):
        return self.settings.get(key, default)
