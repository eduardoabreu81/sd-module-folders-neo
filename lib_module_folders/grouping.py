"""Grouping and ordering of Forge Neo's VAE / Text Encoder list. Pure functions: no Forge import.

Forge lists every file under its VAE and text encoder folders in one list, keyed by filename and sorted by filename,
so the two kinds alternate and the files of one subfolder end up apart. Here each file is told apart by the folder it
came from, and the list is ordered VAE first, then text encoders, each by subfolder and then by filename.
"""

import os

VAE, TEXT_ENCODER, OTHER = "vae", "text_encoder", "other"
GROUP_ORDER = (VAE, TEXT_ENCODER, OTHER)

LABELS = {
    "short": {VAE: "VAE", TEXT_ENCODER: "TE", OTHER: "?"},
    "long": {VAE: "VAE", TEXT_ENCODER: "Text Encoder", OTHER: "?"},
}
SEPARATOR = " · "


def _norm(path):
    return os.path.normcase(os.path.abspath(path))


def _is_under(path, root):
    try:
        return os.path.commonpath([_norm(path), _norm(root)]) == _norm(root)
    except ValueError:  # another drive on Windows
        return False


def kind_of(path, vae_roots, text_encoder_roots):
    """VAE or TEXT_ENCODER by the folder the file was found in; the deepest matching folder wins, so a text encoder
    folder kept inside the VAE folder (or the other way round) still counts as its own kind."""
    best, best_len = OTHER, -1
    for kind, roots in ((VAE, vae_roots), (TEXT_ENCODER, text_encoder_roots)):
        for root in roots:
            if root and _is_under(path, root) and len(_norm(root)) > best_len:
                best, best_len = kind, len(_norm(root))
    return best


def _sort_key(relpath):
    """Subfolder first, filename second, case-insensitive. Files at the top of a folder come before its subfolders."""
    parts = relpath.replace("\\", "/").split("/")
    return tuple(p.casefold() for p in parts[:-1]), parts[-1].casefold()


def ordered(module_list, module_map, vae_roots, text_encoder_roots):
    """[(filename, kind)] in display order. module_list: filename -> absolute path; module_map: filename -> path
    relative to its folder (both as Forge builds them)."""
    entries = []
    for filename, path in module_list.items():
        kind = kind_of(path, vae_roots, text_encoder_roots)
        rel = module_map.get(filename, filename)
        entries.append((GROUP_ORDER.index(kind), _sort_key(rel), filename, kind))
    entries.sort()
    return [(filename, kind) for _, _, filename, kind in entries]


def label(kind, shown, style="short"):
    """The text the dropdown shows: the group, then the name Forge would show, with forward slashes."""
    prefix = LABELS.get(style, LABELS["short"])[kind]
    return f"{prefix}{SEPARATOR}{shown.replace(chr(92), '/')}"


def choices(order, module_map, use_short, style="short"):
    """Gradio (label, value) pairs. The value is exactly what Forge itself puts in the dropdown (the filename, or the
    path relative to its folder), so saved presets, the API and Forge's own handlers keep working unchanged."""
    out = []
    for filename, kind in order:
        value = filename if use_short else module_map.get(filename, filename)
        out.append((label(kind, value, style), value))
    return out


def reorder_in_place(mapping, order):
    """Put an OrderedDict in the given key order without replacing the object (Forge imports it by name)."""
    items = [(key, mapping[key]) for key, _ in order if key in mapping]
    rest = [(key, value) for key, value in mapping.items() if key not in dict(items)]
    mapping.clear()
    mapping.update(items + rest)
