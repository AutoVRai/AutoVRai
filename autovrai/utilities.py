import os
import re
import ast
import cv2
import sys
import glob
import torch
import socket
import logging
import warnings
from PIL import Image
from contextlib import contextmanager


@contextmanager
def suppress_output():
    # save the current logger information
    logger = logging.getLogger()
    current_level = logger.getEffectiveLevel()

    # save the current stdout
    original_stdout = sys.stdout

    # redirect stdout to a null file
    sys.stdout = open(os.devnull, "w")

    # suppress most of the logging output
    logger.setLevel(logging.ERROR)

    try:
        yield
    finally:
        # restore the original logger information
        logger.setLevel(current_level)
        # Restore the original stdout
        sys.stdout.close()
        sys.stdout = original_stdout


########################################################################################
###### Special imports for ZoeDepth utilities from the torch.hub cache directory. ######

warnings.filterwarnings("ignore", category=UserWarning, module="torch.hub", lineno=286)

zoedepth_dir = os.path.join(torch.hub.get_dir(), "isl-org_ZoeDepth_main")

if not os.path.exists(zoedepth_dir):
    print(
        "--- AutoVR.ai ---",
        "Did not find the torch.hub cached version of the "
        "ZoeDepth code, downloading now...",
    )
    with suppress_output():
        torch.hub.help("isl-org/ZoeDepth", "ZoeD_NK", force_reload=True)

# Append the path to the ZoeDepth code in the cache directory to sys.path
sys.path.append(zoedepth_dir)

# Now we can import the utility functions from here:
# ~/.cache/torch/hub/isl-org_ZoeDepth_main/zoedepth/utils/misc.py
from zoedepth.utils.misc import save_raw_16bit, colorize


def colorize_depthmap(depth):
    return colorize(depth, cmap="gray_r")


def save_depthraw(depth, filepath):
    with suppress_output():
        save_raw_16bit(depth, filepath)


###### Special imports for ZoeDepth utilities from the torch.hub cache directory. ######
########################################################################################


def find_filenames(location, patterns):
    # Check if directory exists
    if not os.path.exists(location):
        raise FileNotFoundError(f"Directory does not exist: {location}")

    # List to store image file names
    filenames = []

    # Convert patterns to a list if it came in as a string
    if isinstance(patterns, str):
        patterns = ast.literal_eval(patterns)

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
        config.get("output-stereo"),
        config.get("output-padded"),
        config.get("output-anaglyph"),
        config.get("output-depthmap"),
        config.get("output-depthraw"),
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


# interprets the values in the standard CUDA memory error message, outputs in GB
def parse_memory_error(message):
    info = {}
    matches = re.findall(r"(\d+\.\d+)( GiB| MiB)", message)
    units = {" GiB": 1.074, " MiB": 0.001074}  # Conversion factors to GB

    keys = ["attempted", "total", "allocated", "free", "reserved"]
    for i, match in enumerate(matches):
        value, unit = match
        info[keys[i]] = round(float(value) * units[unit], 2)

    return info


def get_local_ip():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        # doesn't even have to be reachable
        s.connect(("10.255.255.255", 1))
        IP = s.getsockname()[0]
    except Exception:
        IP = "127.0.0.1"
    finally:
        s.close()
    return IP
