import json
import os
import sys
import time
from pathlib import Path
from typing import Dict, Any, List

import requests
from dotenv import load_dotenv
from PIL import Image
from io import BytesIO
from tqdm import tqdm


# Constants - Use relative paths from script location
SCRIPT_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = SCRIPT_DIR.parent
PROMPT_FILE = SCRIPT_DIR / "ai_image_prompts.json"
OUTPUT_DIR = PROJECT_ROOT / "public" / "images"
MODEL_ID = "stabilityai/stable-diffusion-2-1"
ENDPOINT = f"https://api-inference.huggingface.co/models/{MODEL_ID}"
ENV_TOKEN_KEY = "HF_API_TOKEN"
MAX_RETRIES = 3
RETRY_DELAY = 5  # seconds
TARGET_SIZE = (1200, 630)


class GenerationError(Exception):
    """Raised when image generation fails after retries."""


def load_token() -> str:
    """Load HF token from environment or .env file.

    Returns an empty string when unset so callers can choose a fallback path
    (e.g., local/demo generation) instead of failing early.
    """
    load_dotenv()
    return os.getenv(ENV_TOKEN_KEY, "")


def load_prompts() -> Dict[str, Any]:
    if not PROMPT_FILE.exists():
        raise FileNotFoundError(f"Prompt file not found: {PROMPT_FILE}")
    with PROMPT_FILE.open("r", encoding="utf-8") as f:
        return json.load(f)


def ensure_output_dir() -> None:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)


def generate_image(prompt: str, token: str) -> bytes:
    headers = {"Authorization": f"Bearer {token}"}
    payload = {"inputs": prompt, "options": {"wait_for_model": True}}
    err_msg = "Service unavailable"

    for attempt in range(1, MAX_RETRIES + 1):
        try:
            response = requests.post(ENDPOINT, headers=headers, json=payload, timeout=180)

            if response.status_code == 200 and response.headers.get("content-type", "").startswith(
                "image"
            ):
                return response.content

            # Handle common failures
            if response.status_code in {503, 529}:  # model loading / rate limited
                err_msg = f"Service unavailable (HTTP {response.status_code})"
                time.sleep(RETRY_DELAY * attempt)
                continue

            # Unexpected error
            err_msg = response.text
            time.sleep(RETRY_DELAY * attempt)

        except requests.exceptions.RequestException as e:
            # Handle network errors (timeout, DNS, connection reset, etc.)
            err_msg = f"Network error: {str(e)}"
            if attempt < MAX_RETRIES:
                time.sleep(RETRY_DELAY * attempt)
                continue
            # Re-raise on last attempt
            raise GenerationError(f"Generation failed after {MAX_RETRIES} attempts: {err_msg}")

    raise GenerationError(f"Generation failed after {MAX_RETRIES} attempts: {err_msg}")


def generate_placeholder(prompt: str) -> Image.Image:
    """Create a simple placeholder image embedding the prompt text.

    This is a fallback when HF_API_TOKEN is unavailable; keeps the pipeline
    producing the expected files while signaling that the content is a demo.
    """
    img = Image.new("RGB", TARGET_SIZE, color=(24, 24, 34))
    from PIL import ImageDraw, ImageFont

    draw = ImageDraw.Draw(img)
    # Try to load a default font; Pillow ships with DejaVu.
    try:
        font = ImageFont.truetype("DejaVuSans.ttf", 34)
    except Exception:
        font = ImageFont.load_default()

    margin = 32
    title = "DEMO IMAGE"
    draw.text((margin, margin), title, fill=(16, 229, 108), font=font)

    # Wrap prompt roughly to fit width.
    max_width = TARGET_SIZE[0] - 2 * margin
    words = prompt.split()
    lines, line = [], []
    for w in words:
        test = " ".join(line + [w])
        if draw.textlength(test, font=font) <= max_width:
            line.append(w)
        else:
            lines.append(" ".join(line))
            line = [w]
    if line:
        lines.append(" ".join(line))

    y = margin + 50
    for l in lines:
        draw.text((margin, y), l, fill=(220, 220, 220), font=font)
        y += font.size + 4

    return img


def resize_to_thumbnail(content: bytes) -> Image.Image:
    img = Image.open(BytesIO(content)).convert("RGB")
    return img.resize(TARGET_SIZE, Image.Resampling.LANCZOS)


def save_image(img: Image.Image, filename: str) -> Path:
    path = OUTPUT_DIR / filename
    img.save(path, format="JPEG", quality=90)
    return path


def build_tasks() -> List[str]:
    return [
        "NVDA_blackwell_chip",
        "TSLA_robotaxi",
        "AAPL_premium_iphone",
        "META_business_ai",
        "MSFT_copilot",
    ]


def main() -> int:
    token = load_token()
    try:
        prompts = load_prompts()
        ensure_output_dir()
    except Exception as exc:
        print(f"[setup-error] {exc}")
        return 1

    tasks = build_tasks()
    failures = []

    with tqdm(total=len(tasks), desc="Generating blog images") as bar:
        for key in tasks:
            prompt_info = prompts.get(key)
            if not prompt_info or "stable_diffusion_prompt" not in prompt_info:
                failures.append((key, "Missing stable_diffusion_prompt in JSON"))
                bar.update(1)
                continue

            prompt_text = prompt_info["stable_diffusion_prompt"]
            filename = f"{key.lower()}_ai.jpg"

            try:
                if token:
                    raw = generate_image(prompt_text, token)
                    thumb = resize_to_thumbnail(raw)
                else:
                    # Fallback to placeholder when no token is available.
                    thumb = generate_placeholder(prompt_text)
                path = save_image(thumb, filename)
                bar.set_postfix({"saved": path.name})
            except Exception as exc:  # catch generation & save issues
                failures.append((key, str(exc)))
            finally:
                bar.update(1)

    if failures:
        print("\nSome tasks failed:")
        for key, reason in failures:
            print(f" - {key}: {reason}")
        return 1

    print("\nAll images generated to", OUTPUT_DIR)
    return 0


if __name__ == "__main__":
    sys.exit(main())
