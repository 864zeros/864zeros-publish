# LoRA Training Guide — 864zeros Visual Styles

This guide explains how to execute the training pipeline for the two signature 864zeros LoRA models:
1. **`864z_jeff_sketch_v1.safetensors`** (136 sketch images + 136 captions)
2. **`864z_jeff_painting_v1.safetensors`** (150 painting images + 150 captions)

---

## 1. Datasets & Configurations

### **Style A: Jeff Sketch Style (Pencil / Linework / Monochrome)**
* **Training Dataset:** 136 high-resolution sketches + 136 matching `.txt` captions
* **Dataset Archive:** [`media/visuals/training_pools/864z_jeff_sketch_dataset.zip`](../../media/visuals/training_pools/864z_jeff_sketch_dataset.zip) (239.57 MB)
* **Trigger Phrase:** `jeff_sketch style`
* **Base Architecture:** `Stable Diffusion XL 1.0 (SDXL)` / `Flux`
* **Hyperparameter Config:** [`_build/lora/train_config.toml`](train_config.toml)
* **Target Output:** `media/visuals/lora_weights/864z_jeff_sketch_v1.safetensors`

### **Style B: Jeff Painting Style (Oil / Acrylic / Fine Art Color)**
* **Training Dataset:** 150 high-resolution paintings + 150 matching `.txt` captions
* **Dataset Archive:** [`media/visuals/training_pools/864z_jeff_painting_dataset.zip`](../../media/visuals/training_pools/864z_jeff_painting_dataset.zip) (479.33 MB)
* **Trigger Phrase:** `jeff_painting style`
* **Base Architecture:** `Stable Diffusion XL 1.0 (SDXL)` / `Flux`
* **Hyperparameter Config:** [`_build/lora/train_config_paintings.toml`](train_config_paintings.toml)
* **Target Output:** `media/visuals/lora_weights/864z_jeff_painting_v1.safetensors`

---

## 2. 1-Click Training Options

### **Option A: Free Google Colab (100% Free T4 / A100 GPU)**
1. Open Google Colab: **[colab.research.google.com](https://colab.research.google.com/)**
2. Upload and run the Kohya SDXL LoRA trainer notebook (or standard Diffusers LoRA script).
3. Upload either `864z_jeff_sketch_dataset.zip` or `864z_jeff_painting_dataset.zip`.
4. Click **Run All** — training takes ~15–20 minutes on a cloud GPU.
5. Download the resulting `.safetensors` file directly into [`media/visuals/lora_weights/`](../../media/visuals/lora_weights/).

---

### **Option B: 1-Click Cloud LoRA Trainers (Civitai / Replicate / Fal.ai)**
1. Go to **Civitai On-Site Trainer** or **Fal.ai LoRA Trainer**.
2. Upload the desired dataset `.zip`.
3. Set Trigger Word (`jeff_sketch style` or `jeff_painting style`).
4. Click **Train** (takes ~10 minutes).
5. Download the `.safetensors` weight file into `media/visuals/lora_weights/`.

---

## 3. How to Use the Trained LoRAs in Production & Generation

Once weights are placed in `media/visuals/lora_weights/`, you can generate custom illustrations for any practice book, poem, prayer, or scripture lesson:

### **Sketch Generation:**
```text
Prompt:
jeff_sketch style, an old weathered lighthouse standing strong on a rocky cliff in a thunderstorm, dramatic beam of light cutting through dark clouds, expressive cross-hatching, fine graphite pencil on textured paper, high contrast, master draftsmanship
```

### **Painting Generation:**
```text
Prompt:
jeff_painting style, a radiant dawn breaking over rugged coastal cliffs, vibrant acrylic impasto, luminous reflection on ocean water, rich warm oil glazes, textured canvas, expressive brush strokes
```
