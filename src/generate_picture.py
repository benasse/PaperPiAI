import argparse
import feedparser
import json
import os
import random
import re
import shutil
import subprocess


def choose_prompt(filename: str) -> str:
    prompts = []
    with open(filename) as file:
        prompts = json.load(file)
    prompt = random.choice(prompts)
    if re.match(r"^https?://", prompt):
        print(f"[INFO] Detected RSS feed URL: {prompt}")
        feed = feedparser.parse(prompt)

        if not feed.entries:
            raise ValueError(f"No entries found in RSS feed: {prompt}")

        entry = random.choice(feed.entries)
        title = entry.get("title", "").strip()

        if not title:
            raise ValueError(f"No valid title found in RSS feed: {prompt}")
        prompt = title

    return prompt



def choose_style(filename: str) -> str:
    styles = []
    with open(filename) as file:
        styles = json.load(file)
    return random.choice(styles)


parser = argparse.ArgumentParser(description="Generate a new random picture.")
parser.add_argument("output_dir", help="Directory to save the output images")
parser.add_argument("--prompts", default="prompts/flowers.json", help="The prompts file to use")
parser.add_argument("--styles", default="prompts/styles.json", help="The prompts file to use")
parser.add_argument("--prompt", default="", help="The prompt to use")
parser.add_argument("--seed", default=random.randint(1, 10000), help="The seed to use")
parser.add_argument("--steps", default=5, help="The number of steps to perform")
parser.add_argument("--width", default=800, help="The width of the image to generate")
parser.add_argument("--height", default=480, help="The height of the image to generate")
parser.add_argument("--sd", default="OnnxStream/src/build/sd", help="Path to the stable diffusion binary")
parser.add_argument("--model", default="models/stable-diffusion-xl-turbo-1.0-anyshape-onnxstream", help="Path to the stable diffusion model to use")
args = parser.parse_args()

output_dir = args.output_dir
shared_file = 'output.png'

# Select a random subject and art style
prompt = args.prompt
if prompt == '':
    prompt = choose_prompt(args.prompts)
    prompt = prompt + " " + choose_style(args.styles)


# Create a unique argument for the filename
unique_arg = prompt.replace(' ', '_')[:64]
unique_arg = f"{unique_arg}_seed_{args.seed}_steps_{args.steps}_size_{args.width}x{args.height}"
fullpath = os.path.join(output_dir, f"{unique_arg}.png")

# Construct the command
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

# Run the command
print(f"Creating image with prompt '{prompt}'")
print(f"Using seed {args.seed}")
print(f"Saving to {fullpath}")
print(f"Running command:\n{cmd}")
subprocess.run(cmd)
print("Command executed successfully.")

shared_fullpath = os.path.join(output_dir, shared_file)
shutil.copyfile(fullpath, shared_fullpath)
print(f"Copied to {shared_fullpath}")
