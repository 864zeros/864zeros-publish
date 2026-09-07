# 864zeros — 2-Cell SDXL LoRA Training Notebook for Paintings & Fine Art
# Target Output: 864z_jeff_painting_v1.safetensors

# ==========================================
# CELL 1: Environment Setup & Dependencies
# ==========================================
"""
# Run this cell first to set up the Kohya SD-Scripts environment on GPU.
!nvidia-smi

# 1. Clone Kohya SD-Scripts repository
!git clone https://github.com/kohya-ss/sd-scripts.git /content/sd-scripts

# 2. Install PyTorch & Accelerate & LoRA dependencies
%cd /content/sd-scripts
!pip install -q --upgrade pip
!pip install -q torch==2.1.2+cu121 torchvision==0.16.2+cu121 --extra-index-url https://download.pytorch.org/whl/cu121
!pip install -q --upgrade -r requirements.txt
!pip install -q xformers==0.0.23.post1 --index-url https://download.pytorch.org/whl/cu121
!pip install -q bitsandbytes toml huggingface_hub

# 3. Create workspace directories
!mkdir -p /content/dataset/paintings
!mkdir -p /content/output
!mkdir -p /content/sample

print("\n Environment Setup Complete! Ready for Cell 2.")
"""

# =========================================================================
# CELL 2: Dataset Extraction, SDXL LoRA Training & Automatic Download
# =========================================================================
"""
import os
import shutil
import zipfile
from google.colab import files

# --- 1. Locate and Extract Dataset Zip ---
dataset_zip = "/content/864z_jeff_painting_dataset.zip"

if not os.path.exists(dataset_zip):
    print("Please upload 864z_jeff_painting_dataset.zip using the Colab file browser on the left (or upload below):")
    uploaded = files.upload()
    for fn in uploaded.keys():
        if fn.endswith('.zip'):
            dataset_zip = os.path.join("/content", fn)
            break

print(f"Extracting dataset from: {dataset_zip}...")
extract_dir = "/content/dataset/paintings"
os.makedirs(extract_dir, exist_ok=True)

with zipfile.ZipFile(dataset_zip, 'r') as zip_ref:
    zip_ref.extractall(extract_dir)

all_files = os.listdir(extract_dir)
img_count = len([f for f in all_files if f.lower().endswith(('.jpg', '.jpeg', '.png', '.webp'))])
txt_count = len([f for f in all_files if f.lower().endswith('.txt')])
print(f" Dataset Verified: {img_count} images + {txt_count} caption files ready.")

# --- 2. Write Dataset TOML Configuration ---
toml_config = '''
[general]
enable_bucket = true

[[datasets]]
resolution = 1024
min_bucket_reso = 512
max_bucket_reso = 1536
bucket_reso_steps = 64
bucket_no_upscale = false

  [[datasets.subsets]]
  image_dir = "/content/dataset/paintings"
  num_repeats = 10
  caption_extension = ".txt"
  shuffle_caption = true
  keep_tokens = 1
'''

with open('/content/dataset_config.toml', 'w') as f:
    f.write(toml_config.strip())

print(" Dataset configuration TOML written.")

# --- 3. Execute SDXL LoRA Training ---
%cd /content/sd-scripts

sample_prompts = '''
jeff_painting style, portrait of an elder in meditation, dramatic chiaroscuro lighting, rich warm oil glazes, textured canvas, expressive brush strokes --w 1024 --h 1024 --d 42 --l 7.0 --s 28
jeff_painting style, a radiant dawn breaking over rugged coastal cliffs, vibrant acrylic impasto, luminous reflection on ocean water --w 1024 --h 1024 --d 42 --l 7.0 --s 28
'''
with open('/content/sample_prompts.txt', 'w') as f:
    f.write(sample_prompts.strip())

!accelerate launch --mixed_precision="fp16" --num_cpu_threads_per_process=2 sdxl_train_network.py \
    --pretrained_model_name_or_path="stabilityai/stable-diffusion-xl-base-1.0" \
    --dataset_config="/content/dataset_config.toml" \
    --output_dir="/content/output" \
    --output_name="864z_jeff_painting_v1" \
    --save_model_as="safetensors" \
    --save_precision="fp16" \
    --network_module="networks.lora" \
    --network_dim=32 \
    --network_alpha=16 \
    --network_train_unet_only \
    --learning_rate=1e-4 \
    --unet_lr=1e-4 \
    --optimizer_type="AdamW8bit" \
    --lr_scheduler="cosine_with_restarts" \
    --lr_warmup_steps=100 \
    --max_train_epochs=10 \
    --save_every_n_epochs=2 \
    --mixed_precision="fp16" \
    --gradient_checkpointing \
    --xformers \
    --sample_prompts="/content/sample_prompts.txt" \
    --sample_every_n_epochs=2

# --- 4. Verify & Download Trained Model Weights ---
final_model = "/content/output/864z_jeff_painting_v1.safetensors"
if os.path.exists(final_model):
    size_mb = os.path.getsize(final_model) / (1024 * 1024)
    print(f" TRAINING COMPLETE! Final LoRA size: {size_mb:.2f} MB")
    print("Initiating automatic download to your local machine...")
    files.download(final_model)
    print("When downloaded, place '864z_jeff_painting_v1.safetensors' into:")
    print("C:\\dev\\864zeros-publish\\media\\visuals\\lora_weights\\")
else:
    print("Model file not found. Check output directory:")
    print(os.listdir("/content/output"))
"""
