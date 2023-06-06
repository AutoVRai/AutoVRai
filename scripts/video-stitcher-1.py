import cv2
import os
import re
import glob
import argparse
from tqdm import trange


def extract_number(filename):
    # Extract the number from a filename.
    number = re.search(r'\d+', filename)
    if number:
        return int(number.group())
    else:
        return None

def find_filenames(location, patterns):
    # Check if directory exists
    if not os.path.exists(location):
        return "Directory does not exist."

    # List to store image file names
    filenames = []

    # Iterate over patterns and append matching files to the list
    for pattern in patterns:
        filenames.extend(glob.glob(os.path.join(location, pattern)))

    # Return the sorted list of image files
    return sorted(filenames), len(filenames)


def create_video_from_images(input_folder, output_video, fps):
    # Get the list of file names
    filenames, file_count = find_filenames(input_folder, ['*.png', '*.jpg', '*.jpeg'])

    # Sort the list by the number in each filename
    # filenames.sort(key=extract_number)

    if not filenames:
        print(f"No images found in the input folder: {input_folder}")
        return

    # Read the first image to get dimensions
    frame = cv2.imread(filenames[0])
    height, width, _ = frame.shape

    # Define the codec and create VideoWriter object
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    video_writer = cv2.VideoWriter(output_video, fourcc, fps, (width, height))

    # Add each image as a frame
    for i in trange(file_count):
        frame = cv2.imread(filenames[i])
        video_writer.write(frame)

    # Release the VideoWriter object
    video_writer.release()

def main():
    parser = argparse.ArgumentParser(description="Create a video from a set of PNG images.")
    parser.add_argument("input_folder", help="The path to the input folder containing PNG images.")
    parser.add_argument("output_video", help="The path to the output video file.")
    parser.add_argument("--fps", type=int, default=30, help="Frames per second (default: 30)")
    # parser.add_argument("--ignore-numbers", type=bool, default=30, help="Frames per second (default: 30)")

    args = parser.parse_args()

    create_video_from_images(args.input_folder, args.output_video, args.fps)

if __name__ == "__main__":
    main()
