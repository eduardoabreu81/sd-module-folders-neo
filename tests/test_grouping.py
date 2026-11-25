"""Grouping, ordering and the refresh_models wrapper, with stand-ins for Forge Neo's main_entry."""

import os
import sys
import tempfile
import types
import unittest
from collections import OrderedDict

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from lib_module_folders import grouping, patch  # noqa: E402

# the files from the issue that asked for this (Haoming02/sd-webui-forge-classic#1664), as (folder, relative path)
FILES = [
    ("VAE", "flux/ae.safetensors"),
    ("text_encoder", "flux/clip_l.safetensors"),
    ("VAE", "h3/minimax_h3_audio_vae_fp32.safetensors"),
    ("VAE", "h3/minimax_h3_video_vae_fp16.safetensors"),
    ("text_encoder", "h3/qwen3vl_32b_minimax_h3_int4_convrot.safetensors"),
    ("text_encoder", "krea/qwen_3_4b.safetensors"),
    ("VAE", "qwen/qwen_image_vae.safetensors"),
    ("VAE", "sdxl/sdxl_vae.safetensors"),
    ("text_encoder", "flux/t5xxl_fp8_e4m3fn.safetensors"),
    ("VAE", "Loose_vae.safetensors"),
]


def forge_lists(models):
    """module_list and module_map as Forge's refresh_models builds them: keyed by filename, sorted by filename."""
    module_list, module_map = {}, {}
    for folder, rel in FILES:
        path = os.path.join(models, folder, *rel.split("/"))
        name = os.path.basename(path)
        module_list[name] = path
        module_map[name] = os.path.normpath(rel)
    return (OrderedDict((k, module_list[k]) for k in sorted(module_list)),
            OrderedDict((k, module_map[k]) for k in sorted(module_map)))


class GroupingTests(unittest.TestCase):
    def setUp(self):
        self.models = os.path.abspath(os.path.join(tempfile.gettempdir(), "mf-models"))
        self.vae = [os.path.join(self.models, "VAE")]
        self.te = [os.path.join(self.models, "text_encoder")]
        self.module_list, self.module_map = forge_lists(self.models)

    def order(self):
        return grouping.ordered(self.module_list, self.module_map, self.vae, self.te)

    def test_vae_first_then_text_encoders_each_by_folder(self):
        names = [name for name, _ in self.order()]
        self.assertEqual(names, [
            "Loose_vae.safetensors",  # files at the top of the folder come before its subfolders
            "ae.safetensors",
            "minimax_h3_audio_vae_fp32.safetensors",
            "minimax_h3_video_vae_fp16.safetensors",
            "qwen_image_vae.safetensors",
            "sdxl_vae.safetensors",
            "clip_l.safetensors",
            "t5xxl_fp8_e4m3fn.safetensors",
            "qwen3vl_32b_minimax_h3_int4_convrot.safetensors",
            "qwen_3_4b.safetensors",
        ])
        kinds = [kind for _, kind in self.order()]
        self.assertEqual(kinds, [grouping.VAE] * 6 + [grouping.TEXT_ENCODER] * 4)

    def test_labels_change_and_values_stay_forges(self):
        order = self.order()
        full = grouping.choices(order, self.module_map, use_short=False)
        self.assertEqual(full[1], ("VAE · flux/ae.safetensors", os.path.normpath("flux/ae.safetensors")))
        self.assertEqual(sorted(value for _, value in full), sorted(self.module_map.values()))
        short = grouping.choices(order, self.module_map, use_short=True)
        self.assertEqual(short[6], ("TE · clip_l.safetensors", "clip_l.safetensors"))
        self.assertEqual(sorted(value for _, value in short), sorted(self.module_list))

    def test_extra_folders_and_nested_folders(self):
        extra_te = os.path.join(self.models, "VAE", "encoders")  # a --text-encoder-dirs inside the VAE folder
        self.assertEqual(grouping.kind_of(os.path.join(extra_te, "t5.safetensors"), self.vae, self.te + [extra_te]),
                         grouping.TEXT_ENCODER)
        self.assertEqual(grouping.kind_of(os.path.join(self.models, "elsewhere", "x.safetensors"), self.vae, self.te),
                         grouping.OTHER)

    def test_reorder_keeps_the_same_dict_object(self):
        mapping = self.module_map
        grouping.reorder_in_place(mapping, self.order())
        self.assertIs(mapping, self.module_map)
        self.assertEqual(list(mapping)[0], "Loose_vae.safetensors")
        self.assertEqual(len(mapping), len(FILES))


class PatchTests(unittest.TestCase):
    def setUp(self):
        self.models = os.path.abspath(os.path.join(tempfile.gettempdir(), "mf-models"))
        module_list, module_map = forge_lists(self.models)
        main_entry = types.SimpleNamespace(module_list=OrderedDict(), module_map=OrderedDict())

        def refresh_models():
            main_entry.module_list.clear()
            main_entry.module_map.clear()
            main_entry.module_list.update(module_list)
            main_entry.module_map.update(module_map)
            return ["model.safetensors"], list(module_map.values())

        main_entry.refresh_models = refresh_models
        self.main_entry = main_entry
        self.paths = types.SimpleNamespace(models_path=self.models)
        self.shared = types.SimpleNamespace(cmd_opts=types.SimpleNamespace(vae_dirs=[], text_encoder_dirs=[]),
                                            opts=types.SimpleNamespace(sd_modules_dropdown_use_short=False))
        self.enabled = True

    def install(self):
        return patch.install(self.main_entry, self.shared, self.paths, lambda: self.enabled)

    def test_the_wrapper_groups_and_reorders_forges_dicts(self):
        self.assertTrue(self.install())
        ckpts, choices = self.main_entry.refresh_models()
        self.assertEqual(ckpts, ["model.safetensors"])
        self.assertTrue(choices[0][0].startswith("VAE · "))
        self.assertTrue(choices[-1][0].startswith("TE · "))
        # Forge's dicts follow the same order, for the Hires dropdown and preset loading
        self.assertEqual(list(self.main_entry.module_map.values()), [value for _, value in choices])

    def test_installing_twice_wraps_forges_function_once(self):
        original = self.main_entry.refresh_models
        self.install()
        self.install()
        self.assertIs(self.main_entry.refresh_models.__wrapped__, original)

    def test_turned_off_gives_forges_own_list(self):
        self.install()
        self.enabled = False
        _, choices = self.main_entry.refresh_models()
        self.assertTrue(all(isinstance(c, str) for c in choices))

    def test_an_error_falls_back_to_forges_list(self):
        self.install()
        self.shared.cmd_opts = None  # anything that breaks inside the wrapper
        self.paths.models_path = None
        with self.assertLogs("module_folders", level="WARNING"):
            _, choices = self.main_entry.refresh_models()
        self.assertTrue(all(isinstance(c, str) for c in choices))


if __name__ == "__main__":
    unittest.main()
