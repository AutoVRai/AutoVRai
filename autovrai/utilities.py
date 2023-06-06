import os
import glob
import json
import jsonschema
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


def prep_directories(directories: list[str]):
    for directory in directories:
        # Skip empty directories
        if directory == '' or directory is None:
            continue

        # Check if directory exists, create it if not
        if not os.path.exists(directory):
            os.makedirs(directory)

        # Double check that the directory exists now
        if not os.path.exists(directory):
            raise FileNotFoundError(f"Directory could not be created: {directory}")

