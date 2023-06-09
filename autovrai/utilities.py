import os
import cv2
import glob
from PIL import Image


def find_filenames(location, patterns):
    # Check if directory exists
    if not os.path.exists(location):
        raise FileNotFoundError(f"Directory does not exist: {location}")

    # List to store image file names
    filenames = []

    # Iterate over patterns and append matching files to the list
    for pattern in patterns:
        filenames.extend(glob.glob(os.path.join(location, pattern)))

    # Return the sorted list of image files
    return sorted(filenames)


def load_image(filename):
    # Check if file exists
    if not os.path.exists(filename):
        raise FileNotFoundError(f"Image file does not exist: {filename}")

    # Load the image
    image = Image.open(filename)

    # Return the image
    return image


def load_video(filename):
    # Check if file exists
    if not os.path.exists(filename):
        raise FileNotFoundError(f"Video file does not exist: {filename}")

    # Load the video
    video = cv2.VideoCapture(filename)

    if not video.isOpened():
        raise Exception(f"Video file could not be opened: {filename}")

    # Return the image
    return video


def prep_directories(config):
    # Get the list of directories from the config
    directories = [
        config["output-stereo"],
        config["output-padded"],
        config["output-anaglyph"],
        config["output-depthmap"],
        config["output-depthraw"],
    ]

    for directory in directories:
        # Skip empty directories
        if directory == "" or directory is None:
            continue

        # Check if directory exists, create it if not
        if not os.path.exists(directory):
            os.makedirs(directory)

        # Double check that the directory exists now
        if not os.path.exists(directory):
            raise FileNotFoundError(f"Directory could not be created: {directory}")


def determine_file_or_path(file_or_path, context):
    if os.path.isfile(file_or_path):
        return "file"
    elif os.path.isdir(file_or_path):
        return "path"
    else:
        raise ValueError(
            f"Problem determining if {context} is file or directory. "
            f"({context}: {file_or_path})"
        )
