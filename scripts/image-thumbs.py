import os
import argparse
from PIL import Image
from tqdm import trange


def generate_thumbnail(image_path, output_dir, half=None):
    img = Image.open(image_path)
    width, height = img.size

    if half == "left":
        img = img.crop((0, 0, width // 2, height))
    elif half == "right":
        img = img.crop((width // 2, 0, width, height))

    img.thumbnail((128, 128))
    img.save(os.path.join(output_dir, os.path.basename(image_path)))


def main():
    parser = argparse.ArgumentParser(description="Generate thumbnail previews of images in a directory.")

    parser.add_argument("input_dir", help="Input directory containing images.")
    parser.add_argument("--output_dir", help="Output directory for thumbnails. Default: input_dir/thumbs - WARNING: This could overwrite existing files.")
    parser.add_argument("--half", choices=["left", "right"], help="Specify which half of the image to use for thumbnail generation. Accepts 'left' or 'right'.")

    args = parser.parse_args()

    if not args.output_dir:
        args.output_dir = os.path.join(args.input_dir, "thumbs")
    elif args.output_dir == args.input_dir:
        print("ERROR: Input and output directories cannot be the same. The original images would be overwritten. Exiting.")
        return

    if not os.path.exists(args.output_dir):
        os.makedirs(args.output_dir)

    valid_extensions = [".png", ".jpg", ".jpeg"]
    image_files = [f for f in os.listdir(args.input_dir) if os.path.splitext(f)[1].lower() in valid_extensions]

    for i in trange(len(image_files)):
        image_path = os.path.join(args.input_dir, image_files[i])
        generate_thumbnail(image_path, args.output_dir, args.half)


if __name__ == "__main__":
    main()
