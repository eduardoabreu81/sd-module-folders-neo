"""Wraps Forge Neo's main_entry.refresh_models so the VAE / Text Encoder dropdown comes grouped and ordered.

refresh_models() rebuilds main_entry.module_list (filename -> path) and main_entry.module_map (filename -> path relative
to its folder) and returns the dropdown choices. The wrapper lets it run as it is, then:
- puts both dicts in grouped order, in place, so everything else that reads them (the Hires VAE / Text Encoder
  dropdown, preset loading) follows the same order;
- returns (label, value) choices whose value is what Forge would have returned, so only the text on screen changes.
Any error falls back to Forge's own result.
"""

import logging
import os

from lib_module_folders import grouping

logger = logging.getLogger("module_folders")

ATTR_ORIGINAL = "_module_folders_original"


def _roots(paths, cmd_opts):
    vae = [os.path.join(paths.models_path, "VAE"), *(getattr(cmd_opts, "vae_dirs", None) or [])]
    text_encoder = [os.path.join(paths.models_path, "text_encoder"), *(getattr(cmd_opts, "text_encoder_dirs", None) or [])]
    return vae, text_encoder


def grouped_refresh(main_entry, original, shared, paths, settings):
    """The replacement for refresh_models. settings() -> (enabled, label style)."""

    def refresh_models(*args, **kwargs):
        result = original(*args, **kwargs)
        try:
            enabled, style = settings()
            if not enabled:
                return result
            ckpt_list, _ = result
            vae_roots, te_roots = _roots(paths, shared.cmd_opts)
            order = grouping.ordered(main_entry.module_list, main_entry.module_map, vae_roots, te_roots)
            grouping.reorder_in_place(main_entry.module_list, order)
            grouping.reorder_in_place(main_entry.module_map, order)
            use_short = bool(getattr(shared.opts, "sd_modules_dropdown_use_short", True))
            return ckpt_list, grouping.choices(order, main_entry.module_map, use_short, style)
        except Exception as exc:  # never break Forge's model list
            logger.warning("Module Folders: keeping Forge's own VAE / Text Encoder list (%s: %s)", type(exc).__name__, exc)
            return result

    refresh_models.__wrapped__ = original
    setattr(refresh_models, ATTR_ORIGINAL, original)
    return refresh_models


def install(main_entry, shared, paths, settings):
    """Replace main_entry.refresh_models once; a UI reload re-imports the script and must not wrap the wrapper."""
    current = getattr(main_entry, "refresh_models", None)
    if current is None:
        logger.warning("Module Folders: this Forge has no main_entry.refresh_models; the dropdown stays as it is")
        return False
    original = getattr(current, ATTR_ORIGINAL, current)
    main_entry.refresh_models = grouped_refresh(main_entry, original, shared, paths, settings)
    return True
