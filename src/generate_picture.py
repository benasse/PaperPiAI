import argparse
import feedparser
import json
import os
import random
import re
import shutil
import subprocess
from PIL import Image, ImageDraw, ImageFont


def choose_prompt(filename: str) -> tuple[str, str]:
    """Return a tuple (prompt, source_url)"""
    with open(filename, encoding="utf-8") as file:
        prompts = json.load(file)
    prompt = random.choice(prompts)
    source_url = ""

    # If prompt is actually an RSS URL
    if re.match(r"^https?://", prompt):
        print(f"[INFO] Detected RSS feed URL: {prompt}")
        source_url = prompt
        feed = feedparser.parse(prompt)

        if not feed.entries:
            raise ValueError(f"No entries found in RSS feed: {prompt}")

        entry = random.choice(feed.entries)
        title = entry.get("title", "").strip()

        if not title:
            raise ValueError(f"No valid title found in RSS feed: {prompt}")
        prompt = title

    return prompt, source_url


def choose_style(filename: str) -> str:
    """Pick a random style from a JSON file."""
    with open(filename, encoding="utf-8") as file:
        styles = json.load(file)
    return random.choice(styles)


def draw_text_with_outline(draw, position, text, font, fill, outline, outline_width=1):
    """Draw text with outline."""
    x, y = position
    for dx in range(-outline_width, outline_width + 1):
        for dy in range(-outline_width, outline_width + 1):
            if dx != 0 or dy != 0:
                draw.text((x + dx, y + dy), text, font=font, fill=outline)
    draw.text((x, y), text, font=font, fill=fill)


def add_prompt_to_image(image_path: str, prompt: str, source: str = None):
    """Overlay the prompt and optional source on the image."""
    img = Image.open(image_path)
    draw = ImageDraw.Draw(img)
    font_size = max(16, img.width // 40)

    # Load font supporting accented characters
    try:
        font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", font_size)
    except Exception:
        font = ImageFont.load_default()

    main_color = (255, 255, 0)    # Yellow
    outline_color = (0, 0, 0)     # Black
    source_color = (200, 200, 200)  # Light gray

    margin = 10
    line_height = font_size + 6

    # Wrap text every 60 chars (approx)
    prompt_lines = [prompt[i:i + 60] for i in range(0, len(prompt), 60)]
    text_block_height = line_height * len(prompt_lines)
    if source:
        text_block_height += line_height

    # Make sure text is not cropped
    y = img.height - text_block_height - margin
    if y < margin:
        y = margin

    # Draw prompt lines
    for line in prompt_lines:
        draw_text_with_outline(draw, (margin, y), line, font, main_color, outline_color, 1)
        y += line_height

    # Draw source if any (with outline too)
    if source:
        source_text = f"Source: {source}"
        draw_text_with_outline(draw, (margin, y), source_text, font, source_color, outline_color, 1)

    img.save(image_path)


# --- CLI arguments ---
parser = argparse.ArgumentParser(description="Generate a new random picture.")
parser.add_argument("output_dir", help="Directory to save the output images")
parser.add_argument("--prompts", default="prompts/flowers.json", help="The prompts file to use")
parser.add_argument("--styles", default="prompts/styles.json", help="The styles file to use")
parser.add_argument("--prompt", default="", help="The prompt to use")
parser.add_argument("--seed", type=int, default=random.randint(1, 10000), help="The seed to use")
parser.add_argument("--steps", type=int, default=5, help="The number of steps to perform")
parser.add_argument("--width", type=int, default=800, help="The width of the image to generate")
parser.add_argument("--height", type=int, default=480, help="The height of the image to generate")
parser.add_argument("--sd", default="OnnxStream/src/build/sd", help="Path to the stable diffusion binary")
parser.add_argument("--model", default="models/stable-diffusion-xl-turbo-1.0-anyshape-onnxstream", help="Path to the stable diffusion model to use")
args = parser.parse_args()

os.makedirs(args.output_dir, exist_ok=True)

# --- Choose prompt & style ---
prompt = args.prompt
source_url = ""
if not prompt:
    prompt, source_url = choose_prompt(args.prompts)
    prompt = prompt + " " + choose_style(args.styles)

# --- Unique file names ---
safe_prompt = re.sub(r'[^a-zA-Z0-9_-]', '_', prompt)[:64]
unique_arg = f"{safe_prompt}_seed_{args.seed}_steps_{args.steps}_size_{args.width}x{args.height}"
fullpath = os.path.join(args.output_dir, f"{unique_arg}.png")

# --- Generate image ---
cmd = [
    args.sd,
    "--xl", "--turbo",
    "--models-path", args.model,
    "--rpi-lowmem",
    "--prompt", prompt,
    "--seed", str(args.seed),
    "--output", fullpath,
    "--steps", str(args.steps),
    "--res", f"{args.width}x{args.height}"
]

print(f"🖼️  Creating image with prompt: {prompt}")
print(f"🎲  Seed: {args.seed}")
print(f"💾  Saving to: {fullpath}")
print(f"⚙️  Running command:\n{' '.join(cmd)}")

subprocess.run(cmd, check=True)
print("✅ Command executed successfully.")

# --- Add prompt overlay ---
fullpath_prompt = os.path.join(args.output_dir, f"{unique_arg}_with_prompt.png")
shutil.copyfile(fullpath, fullpath_prompt)
add_prompt_to_image(fullpath_prompt, prompt, source_url)
print(f"🖋️  Image with prompt saved to: {fullpath_prompt}")

# --- Save text file ---
txt_file = os.path.join(args.output_dir, f"{unique_arg}.txt")
with open(txt_file, "w", encoding="utf-8") as f:
    f.write(f"Prompt: {prompt}\n")
    if source_url:
        f.write(f"Source: {source_url}\n")
print(f"📝 Prompt written to: {txt_file}")

# --- Copy shared output ---
shared_path = os.path.join(args.output_dir, "output.png")
shutil.copyfile(shared_path, shared_path)
print(f"📤 Copied to {shared_path}")
