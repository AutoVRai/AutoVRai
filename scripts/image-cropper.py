import os
import argparse
from PIL import Image
from tqdm import trange

def process_images(input_dir, output_dir, crop_width, crop_height, crop_alignment, final_width, final_height):
    if final_width % 32 != 0 or final_height % 32 != 0:
        print("Warning: Final width or height can't be evenly divided by 32.")

    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    image_files = [f for f in os.listdir(input_dir) if f.lower().endswith(('.png', '.jpg', '.jpeg'))]
    for i in trange(len(image_files)):
        image_file = image_files[i]
        input_path = os.path.join(input_dir, image_file)
        output_path = os.path.join(output_dir, image_file)

        with Image.open(input_path) as img:
            img_width, img_height = img.size

            if crop_alignment == 'left':
                left = 0
            elif crop_alignment == 'right':
                left = img_width - crop_width
            else:
                left = (img_width - crop_width) // 2

            top = (img_height - crop_height) // 2
            img_cropped = img.crop((left, top, left + crop_width, top + crop_height))

            img_final = Image.new('RGB', (final_width, final_height), color='black')
            img_final.paste(img_cropped, ((final_width - crop_width) // 2, (final_height - crop_height) // 2))
            img_final.save(output_path)

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Process images for AutoVR.ai')
    parser.add_argument('input_dir', help='Input directory containing PNG or JPG files')
    parser.add_argument('output_dir', help='Output directory for processed images')
    parser.add_argument('crop_width', type=int, help='Width of the cropped portion of the image')
    parser.add_argument('crop_height', type=int, help='Height of the cropped portion of the image')
    parser.add_argument('crop_alignment', choices=['left', 'right', 'center'], help='Alignment option for cropping')
    parser.add_argument('final_width', type=int, help='Final width of the resulting image')
    parser.add_argument('final_height', type=int, help='Final height of the resulting image')

    args = parser.parse_args()
    process_images(args.input_dir, args.output_dir, args.crop_width, args.crop_height, args.crop_alignment, args.final_width, args.final_height)
