import os
import time
import numpy as np
from tqdm import trange
from PIL import Image
from collections import namedtuple

import autovrai


def process_single_video(model: autovrai.ZoeDepth_DepthModel, config, video):
    print(
        "This will be implemented soon in another version, but for now you can use the "
        "video shredder and video stitcher from the scripts directory."
    )
    pass


def process_video_directory(model: autovrai.ZoeDepth_DepthModel, config):
    autovrai.prep_directories(config)
    print(
        "This will be implemented soon in another version, but for now you can use the "
        "video shredder and video stitcher from the scripts directory."
    )
    pass


def process_single_image(model: autovrai.ZoeDepth_DepthModel, config, image):
    print(
        "This is only used by the GUI interface and will be implemented soon in "
        "another version, but you can place a single image in the input directory."
    )
    pass


def process_image_directory(model: autovrai.ZoeDepth_DepthModel, config):
    autovrai.prep_directories(config)

    filenames = autovrai.find_filenames(
        config["input-source"], config["input-patterns"]
    )
    file_count = filenames.__len__()

    precision = determine_precision_info(config)
    print("--- AutoVR.ai ---", "Using precision:", precision)

    # Add this line before the loop processing thousands of images
    factors = {}

    for i in trange(file_count):
        filename = filenames[i]
        filepath = os.path.basename(filename)

        # load the actual image from the file
        image = autovrai.load_image(filename)

        # determine the initial precision settings to use
        if precision.type == "pixels":
            width = precision.width
            height = precision.height
            factor = 1.0
        elif precision.type == "factor":
            width = image.width
            height = image.height
            factor = precision.factor
        else:
            raise ValueError("Invalid precision type (factor or pixels)")

        # generate the actual depth info either with a manual precision mode that will
        # fail if we run out of VRAM, or dynamically where the precision used will be
        # reduced automatically if an error is encountered
        if precision.mode == "manual":
            autovrai.set_model_precision(model, width, height, factor)
            depth = model.infer_pil(image, output_type="numpy")
        elif precision.mode == "dynamic":
            success = False

            # check if we've already attempted this width and height combination
            dimensions = (width, height)
            if dimensions in factors:
                factor = factors[dimensions]

            # attempt to generate a depth map, but reduce the factor and retry if needed
            while not success and factor > 0:
                try:
                    autovrai.set_model_precision(model, width, height, factor)
                    depth = model.infer_pil(image, output_type="numpy")
                    success = True
                except Exception as e:
                    print(
                        "--- AutoVR.ai ---",
                        f"Error encountered while using "
                        f"(width: {width}), "
                        f"(height: {height}), "
                        f"and (factor: {factor}). "
                        "Retrying with a lower factor...",
                    )
                    time.sleep(1)
                    factor = round(factor - 0.1, 1)

            # once the depth information has been generated, save the final factor used
            if success:
                factors[dimensions] = factor
            else:
                raise RuntimeError(
                    "Failed to generate depth map even after reducing factor to zero."
                )
        else:
            raise ValueError("Invalid precision mode (dynamic or manual)")

        # generate the stereo images for the left and right eyes
        left, right = autovrai.stereo_eyes(image, depth, config["stereo-intensity"])

        # save the outputs based on the output locations defined in the config
        save_image_outputs(config, image, depth, left, right, filepath)

    print(
        "--- AutoVR.ai ---",
        f"Processed {file_count} images. "
        f"The final precision factor settings used: {factors}",
    )


def save_image_outputs(config, image, depth, left, right, filepath):
    if config["output-stereo"] != "":
        stereo = autovrai.combine_stereo(left, right)
        stereo.save(os.path.join(config["output-stereo"], filepath))

    if config["output-padded"] != "":
        padding = determine_padding_info(config)
        if padding.type == "pixels":
            padded = autovrai.combine_padded(
                left,
                right,
                padded.width,
                padded.height,
                padded.color,
            )
        elif padding.type == "factor":
            padded = autovrai.combine_padded(
                left,
                right,
                int(round(image.width * padded.factor)),
                int(round(image.height * padded.factor)),
                padded.color,
            )
        else:
            raise ValueError("Invalid padded type (factor or pixels)")
        padded.save(os.path.join(config["output-padded"], filepath))

    if config["output-anaglyph"] != "":
        anaglyph = autovrai.combine_anaglyph(left, right)
        anaglyph.save(os.path.join(config["output-anaglyph"], filepath))

    if config["output-depthmap"] != "":
        depthmap = Image.fromarray(autovrai.ZoeDepth_colorize(depth, cmap="gray_r"))
        depthmap.save(os.path.join(config["output-depthmap"], filepath))

    if config["output-depthraw"] != "":
        autovrai.ZoeDepth_save_raw_16bit(
            depth, os.path.join(config["output-depthraw"], filepath)
        )


def determine_precision_info(config):
    mode = config.get("precision-mode", "dynamic")
    width = config.get("precision-width", None)
    height = config.get("precision-height", None)
    factor = config.get("precision-factor", None)

    # make sure we don't have conflicting precision settings
    if (factor != None and factor > 0) and (
        (width != None and width > 0) or (height != None and height > 0)
    ):
        raise ValueError(
            "Invalid precision settings. Please use either factor or width/height. "
            "Not both. This should have been caught by the schema validation"
        )

    # just being extra careful here, this should have been caught by the schema
    if width != None and height != None and width > 0 and height > 0:
        type = "pixels"
        factor = None
    elif factor != None and factor > 0:
        type = "factor"
        width = None
        height = None
    else:
        raise ValueError("Invalid precision settings. This shouldn't happen.")

    Precision = namedtuple("Precision", ["type", "mode", "width", "height", "factor"])
    return Precision(type, mode, width, height, factor)


def determine_padding_info(config):
    color = config["padded-color"]
    width = config["padded-width"]
    height = config["padded-height"]
    factor = config["padded-factor"]

    # make sure we don't have conflicting padded settings
    if (factor != None and factor > 0) and (
        (width != None and width > 0) or (height != None and height > 0)
    ):
        raise ValueError(
            "Invalid padded settings. Please use either factor or width/height. "
            "Not both. This should have been caught by the schema validation"
        )

    # just being extra careful here, this should have been caught by the schema
    if width != None and height != None and width > 0 and height > 0:
        type = "pixels"
        factor = None
    elif factor != None and factor > 0:
        type = "factor"
        width = None
        height = None
    else:
        raise ValueError("Invalid padded settings. This shouldn't happen.")

    Padded = namedtuple("Padded", ["type", "color", "width", "height", "factor"])
    return Padded(type, color, width, height, factor)
