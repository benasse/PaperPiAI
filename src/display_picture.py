import argparse
from PIL import Image
from inky.auto import auto
from inky import Inky_Impressions_7 as Inky
import sys
import os

def main():
    parser = argparse.ArgumentParser(
        description="Display an image on the Inky Impression 7 display (auto-rotate if needed)."
    )
    parser.add_argument(
        "image",
        type=str,
        help="Path to the image file to display"
    )
    parser.add_argument(
        "-s", "--saturation",
        type=float,
        default=0.5,
        help="Saturation level for the display (default: 0.5)"
    )
    parser.add_argument(
        "--no-display",
        action="store_true",
        help="Do not send the image to the display (for testing)"
    )

    args = parser.parse_args()

    # --- Validate input ---
    if not os.path.exists(args.image):
        print(f"❌ Error: image file '{args.image}' not found.")
        sys.exit(1)

    # --- Load Inky display ---
    try:
        inky = Inky()
    except Exception as e:
        print(f"❌ Error initializing Inky display: {e}")
        sys.exit(1)

    disp_w, disp_h = inky.resolution
    print(f"🖥️ Loaded Inky display: {disp_w}x{disp_h}, saturation={args.saturation}")

    # --- Open and prepare image ---
    try:
        image = Image.open(args.image)
    except Exception as e:
        print(f"❌ Error loading image: {e}")
        sys.exit(1)

    img_w, img_h = image.size
    print(f"📸 Original image size: {img_w}x{img_h}")

    # --- Auto-detect orientation ---
    img_is_portrait = img_h > img_w
    disp_is_portrait = disp_h > disp_w

    if img_is_portrait != disp_is_portrait:
        print("↻ Rotating image 90° to match display orientation...")
        image = image.rotate(90, Image.NEAREST, expand=True)
    else:
        print("✅ Orientation already matches display.")

    # --- Resize to display resolution ---
    image = image.resize(inky.resolution)
    print(f"📏 Resized to {inky.resolution}")

    # --- Display or simulate ---
    if not args.no_display:
        try:
            inky.set_image(image, saturation=args.saturation)
            inky.show()
            print("✅ Image successfully displayed on Inky Impression.")
        except Exception as e:
            print(f"❌ Error displaying image: {e}")
            sys.exit(1)
    else:
        print("🧪 Display simulation mode: no output sent to Inky.")

if __name__ == "__main__":
    main()
