"""Module Folders for Forge Neo: the VAE / Text Encoder dropdown grouped by kind and ordered by folder.

Only the dropdown's labels and order change. The value behind each choice stays what Forge uses, so presets, the API
and loading are untouched. See lib_module_folders/patch.py.
"""

import os
import sys

from modules import paths, script_callbacks, shared

EXT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if EXT_DIR not in sys.path:
    sys.path.insert(0, EXT_DIR)

from lib_module_folders import patch  # noqa: E402

KEY_ENABLED = "module_folders_enabled"


def _enabled():
    return shared.opts.data.get(KEY_ENABLED, True)


def on_ui_settings():
    from modules.options import OptionInfo, options_section

    options = options_section(("module_folders", "Module Folders", "ui"), {
        KEY_ENABLED: OptionInfo(
            True, "Group the VAE / Text Encoder dropdown: VAE first, then text encoders, each ordered by folder",
        ).info("takes effect with the dropdown's refresh button, or on the next page load"),
    })
    for key, info in options.items():
        shared.opts.add_option(key, info)


try:
    from modules_forge import main_entry
except ImportError as exc:
    print(f"[Module Folders] this is not Forge Neo ({exc}); nothing changed")
else:
    patch.install(main_entry, shared, paths, _enabled)

script_callbacks.on_ui_settings(on_ui_settings, name="module_folders")
