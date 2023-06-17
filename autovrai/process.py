import os
import tqdm
from PIL import Image
from collections import namedtuple


import autovrai


def process_single_video(config, video):
    print(
        "This will be implemented soon in another version, but for now you can use the "
        "video shredder and video stitcher from the scripts directory."
    )
    pass


def process_video_directory(config):
    autovrai.prep_directories(config)
    print(
        "This will be implemented soon in another version, but for now you can use the "
        "video shredder and video stitcher from the scripts directory."
    )
    pass


def process_single_image(config, image):
    print(
        "This is only used by the GUI interface and will be implemented soon in "
        "another version, but you can place a single image in the input directory."
    )
    pass


def process_image_directory(config, progress=None):
    autovrai.prep_directories(config)

    filenames = autovrai.find_filenames(
        config["input-source"], config["input-patterns"]
    )
    file_count = filenames.__len__()

    precision = determine_precision_info(config)
    print("--- AutoVR.ai ---", precision)

    factors = config.get("factors", {})
    print("--- AutoVR.ai ---", "Using factors:", factors)

    # this is the model that will be used to process the images, but it needs
    # reloaded if the precision changes or if we hit an out of memory error
    model = None

    if progress != None:
        current = 0.0
        portion = 1.0 / file_count
        progress(current, desc="Starting...")

    for i in tqdm.trange(file_count):
        filename = filenames[i]
        filepath = os.path.basename(filename)

        # load the actual image from the file
        image = autovrai.load_image(filename)
        depth = None

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

        # track if the current run worked functions as the key to the factors
        # dictionary to track what factors worked
        success = False
        dimensions = str((width, height))

        # check if we have a known factor to use for this width and height combination
        if dimensions in factors:
            factor = factors[dimensions]

        if progress != None and model == None:
            progress(0, desc="Loading model, just a moment...")

        # generate the actual depth info either with a manual precision mode that will
        # fail if we run out of VRAM, or dynamically where the precision used will be
        # reduced automatically if an error is encountered
        if precision.mode == "manual":
            model = autovrai.model_loader(config, width, height, factor)
            depth = model.infer_pil(image, output_type="numpy")
            success = True
        elif precision.mode == "dynamic":
            # attempt to generate a depth map, but reduce the factor and retry if needed
            while not success and factor > 0:
                try:
                    model = autovrai.model_loader(config, width, height, factor)
                    depth = model.infer_pil(image, output_type="numpy")
                    success = True
                except RuntimeError as e:
                    if "out of memory" in str(e) or "can't allocate memory" in str(e):
                        print(
                            "--- AutoVR.ai ---",
                            f"Error encountered while using "
                            f"(width: {width}), "
                            f"(height: {height}), "
                            f"and (factor: {factor}). "
                            "Retrying with a lower factor...",
                        )
                        print(
                            "--- AutoVR.ai ---",
                            "Memory Error (in GB): ",
                            autovrai.parse_memory_error(str(e)),
                        )
                        del depth
                        depth = None
                        model = autovrai.model_unloader(model)
                        factor = round(factor - 0.1, 1)
                    else:
                        raise e
        else:
            raise ValueError("Invalid precision mode (dynamic or manual)")

        # once the depth information has been generated, save the final factor used
        if success:
            factors[dimensions] = factor
        else:
            raise RuntimeError(
                "Failed to generate depth map even after reducing factor to zero."
            )

        # generate the stereo images for the left and right eyes
        left, right = autovrai.stereo_eyes(image, depth, config["stereo-intensity"])

        # save the outputs based on the output locations defined in the config
        save_image_outputs(config, image, depth, left, right, filepath)

        if progress != None:
            current += portion
            progress(current, desc=f"Processed {filepath}")

    print(
        "--- AutoVR.ai ---",
        f"Processed {file_count} images. "
        f"The final precision factor settings used: {factors}",
    )

    # we are done with the model, go ahead and unload it to free up memory
    model = autovrai.model_unloader(model)

    return f"Done. Processed {file_count} images."


def save_image_outputs(config, image, depth, left, right, filepath):
    if config.get("output-stereo"):
        stereo = autovrai.combine_stereo(left, right)
        stereo.save(os.path.join(config["output-stereo"], filepath))

    if config.get("output-padded"):
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

    if config.get("output-anaglyph"):
        anaglyph = autovrai.combine_anaglyph(left, right)
        anaglyph.save(os.path.join(config["output-anaglyph"], filepath))

    if config.get("output-depthmap"):
        depthmap = Image.fromarray(autovrai.colorize_depthmap(depth))
        depthmap.save(os.path.join(config["output-depthmap"], filepath))

    if config.get("output-depthraw"):
        autovrai.save_depthraw(depth, os.path.join(config["output-depthraw"], filepath))


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
    color = config.get("padded-color")
    width = config.get("padded-width")
    height = config.get("padded-height")
    factor = config.get("padded-factor")

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
