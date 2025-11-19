# Hugging Face Stable Diffusion Blog Thumbnails

This script batch-generates 1200×630 blog thumbnails using the Hugging Face Inference API (free tier) and Stable Diffusion.

## Setup
- Python 3.9+
- Install deps: `pip install -r requirements.txt`
- Copy `.env.example` to `.env` and set `HF_API_TOKEN` to your Hugging Face access token (works with free tier).

## Usage
```bash
python scripts/generate_blog_images.py
```

Outputs are saved under `public/images/` with filenames `{slug}_ai.jpg`, e.g. `nvda_blackwell_chip_ai.jpg`.

## What it does
- Loads prompts from `scripts/ai_image_prompts.json` (uses `stable_diffusion_prompt`).
- Generates five images (NVDA, TSLA, AAPL, META, MSFT themes).
- Retries transient API errors (503/529) up to 3 times.
- Resizes to 1200×630 and saves JPEG (quality 90).
- Shows progress via tqdm and prints any failures.

## Notes
- Endpoint: `https://api-inference.huggingface.co/models/stabilityai/stable-diffusion-2-1`
- Customize prompts or task list in `scripts/generate_blog_images.py` (`build_tasks`).
