import cv2
import os
import argparse
import glob

def split_images(input_folder, save_left, save_right):
    image_files = sorted(glob.glob(os.path.join(input_folder, "*.png")))

    if not image_files:
        print(f"No images found in the input folder: {input_folder}")
        return

    if save_left:
        left_output_folder = os.path.join(input_folder, "left")
        os.makedirs(left_output_folder, exist_ok=True)

    if save_right:
        right_output_folder = os.path.join(input_folder, "right")
        os.makedirs(right_output_folder, exist_ok=True)

    for image_file in image_files:
        image = cv2.imread(image_file)
        height, width, _ = image.shape
        mid_width = width // 2

        if save_left:
            left_image = image[:, :mid_width]
            left_output_file = os.path.join(left_output_folder, os.path.basename(image_file))
            cv2.imwrite(left_output_file, left_image)

        if save_right:
            right_image = image[:, mid_width:]
            right_output_file = os.path.join(right_output_folder, os.path.basename(image_file))
            cv2.imwrite(right_output_file, right_image)

def main():
    parser = argparse.ArgumentParser(description="Split images in a directory in half vertically.")
    parser.add_argument("input_folder", help="The path to the input folder containing images.")
    parser.add_argument("--left", action="store_true", help="Save only the left half of the images.")
    parser.add_argument("--right", action="store_true", help="Save only the right half of the images.")

    args = parser.parse_args()

    save_left = args.left or not args.right
    save_right = args.right or not args.left

    split_images(args.input_folder, save_left, save_right)

if __name__ == "__main__":
    main()
