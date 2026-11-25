# 🗂️ Module Folders for Forge Neo

<div align="center">

[![Forge Neo](https://img.shields.io/badge/Forge-Neo-blue)](https://github.com/Haoming02/sd-webui-forge-classic/tree/neo)
[![Gradio](https://img.shields.io/badge/Gradio-4.40.0-orange)](https://gradio.app/)
[![Version](https://img.shields.io/badge/Version-0.1.0-brightgreen)](https://github.com/eduardoabreu81/sd-module-folders-neo)
[![License](https://img.shields.io/badge/License-AGPL--3.0-green.svg)](LICENSE)

> **Extension for [Stable Diffusion WebUI Forge - Neo](https://github.com/Haoming02/sd-webui-forge-classic/tree/neo)**

</div>

With a few models installed, the **VAE / Text Encoder** dropdown turns into one long list: VAEs and text encoders mixed together, sorted by filename, so the files of one folder end up far apart. Module Folders **groups the list**: VAEs first, then text encoders, each **ordered by folder** and then by filename, with the group in front of every name.

| Forge Neo | With Module Folders |
| :--- | :--- |
| `flux/ae.safetensors` | `VAE · Loose_vae.safetensors` |
| `flux/clip_l.safetensors` | `VAE · flux/ae.safetensors` |
| `h3/minimax_h3_audio_vae_fp32.safetensors` | `VAE · h3/minimax_h3_audio_vae_fp32.safetensors` |
| `h3/minimax_h3_video_vae_fp16.safetensors` | `VAE · h3/minimax_h3_video_vae_fp16.safetensors` |
| `h3/qwen3vl_32b_minimax_h3_int4_convrot.safetensors` | `VAE · qwen/qwen_image_vae.safetensors` |
| `krea/qwen_3_4b.safetensors` | `VAE · sdxl/sdxl_vae.safetensors` |
| `Loose_vae.safetensors` | `TE · flux/clip_l.safetensors` |
| `qwen/qwen_image_vae.safetensors` | `TE · flux/t5xxl_fp8_e4m3fn.safetensors` |
| `sdxl/sdxl_vae.safetensors` | `TE · h3/qwen3vl_32b_minimax_h3_int4_convrot.safetensors` |
| `flux/t5xxl_fp8_e4m3fn.safetensors` | `TE · krea/qwen_3_4b.safetensors` |

Asked for in [Haoming02/sd-webui-forge-classic#1664](https://github.com/Haoming02/sd-webui-forge-classic/issues/1664).

> [!Important]
> Only the **text and order** of the dropdown change. The value behind each choice is still the one Forge Neo uses, so your saved presets, the API, infotext and model loading work exactly as before. Turn the extension off and the list is Forge's own again.

---

## 📦 Installation

1. Open Forge Neo and go to **Extensions** → **Install from URL**
2. Paste:

```text
https://github.com/eduardoabreu81/sd-module-folders-neo
```

3. Click **Install** and restart Forge Neo

---

## ⚙️ Settings

In **Settings** → **Module Folders**:

- **Group the VAE / Text Encoder dropdown** (on by default): off gives Forge's own list back.

The change shows up with the dropdown's **refresh** button (🔄) or on the next page load.

Forge's own **Settings** → **UI Alternatives** → **Show filenames without folder in the VAE / Text Encoder dropdown** still decides whether the folder is shown: with it on, the labels read `VAE · ae.safetensors`; the order stays grouped and by folder either way. That setting needs **Reload UI**.

---

## 🔍 How it works

- A file is a **VAE** or a **text encoder** by the folder it was found in: `models/VAE` and `--vae-dirs`, or `models/text_encoder` and `--text-encoder-dirs`. A text encoder folder kept inside the VAE folder still counts as text encoders.
- Inside each group, files at the top of the folder come first, then each subfolder in alphabetical order (case-insensitive), then the files inside it.
- The **Hires VAE / Text Encoder** dropdown follows the same order, without the group labels.

**Not covered:** two files with the same name in different folders. Forge Neo lists modules by filename, so only one of them shows up, with or without this extension.

Under the hood, the extension wraps Forge Neo's `refresh_models()` (`modules_forge/main_entry.py`): Forge builds its list as usual, then the extension reorders it and returns `(label, value)` pairs for the dropdown. If anything goes wrong there, Forge's own list is used and a warning is printed. No Forge Neo file is modified.

---

## 🧪 Tests

```bash
python -m pytest -q tests
```

---

## 📄 License

[AGPL-3.0](LICENSE)

---

<div align="center">

Made with ❤️ for the Stable Diffusion community

**[Report Bug](https://github.com/eduardoabreu81/sd-module-folders-neo/issues)** • **[Request Feature](https://github.com/eduardoabreu81/sd-module-folders-neo/issues)** • **[☕ Ko-fi](https://ko-fi.com/eduardoabreu81)**

</div>
