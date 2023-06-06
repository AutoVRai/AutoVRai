import os
import argparse
from PIL import Image

def place_image(img, new_size, bg_color):
    # Create a new image with the background color and desired size
    new_img = Image.new("I", new_size, bg_color)

    # Calculate the position to paste the original image into the new image
    paste_position = ((new_size[0] - img.size[0]) // 2, (new_size[1] - img.size[1]) // 2)

    # Paste the original image into the new image
    new_img.paste(img, paste_position)

    return new_img

def main(args):
    in_dir = args.input
    out_dir = args.output
    new_size = (args.width, args.height)
    bg_color = args.bg_color if args.bg_color else 0 # 65535 - Maximum value for 16-bit images

    files = [f for f in os.listdir(in_dir) if os.path.isfile(os.path.join(in_dir, f))]

    print(f"Found {len(files)} files to process.")

    for i, file in enumerate(files, start=1):
        with Image.open(os.path.join(in_dir, file)) as img:
            new_img = place_image(img, new_size, bg_color)
            new_img.save(os.path.join(out_dir, file), "PNG")
        if i % 10 == 0:
            print(f"Processed {i} files...")

    print("All done!")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Center images.')
    parser.add_argument('input', type=str, help='Input directory')
    parser.add_argument('output', type=str, help='Output directory')
    parser.add_argument('height', type=int, help='New image height')
    parser.add_argument('width', type=int, help='New image width')
    parser.add_argument('--bg_color', type=int, help='Background color for depth map (default: 0 for 16-bit images)')

    args = parser.parse_args()
    main(args)
