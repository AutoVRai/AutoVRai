import os
import numpy as np
from tqdm import trange
from PIL import Image

import autovrai


def process_single_video(config, model: autovrai.ZoeDepth_DepthModel, video):
    print(
        "This will be implemented soon in another version, but for now you can use the "
        "video shredder and video stitcher from the scripts directory."
    )
    pass


def process_video_directory(config, model: autovrai.ZoeDepth_DepthModel):
    autovrai.prep_directories(config)
    print(
        "This will be implemented soon in another version, but for now you can use the "
        "video shredder and video stitcher from the scripts directory."
    )
    pass


def process_single_image(config, model: autovrai.ZoeDepth_DepthModel, image):
    pass


def set_precision(model: autovrai.ZoeDepth_DepthModel, width, height):
    model.core.prep.resizer._Resize__width = width
    model.core.prep.resizer._Resize__height = height


def process_image_directory(config, model: autovrai.ZoeDepth_DepthModel):
    autovrai.prep_directories(config)

    filenames = autovrai.find_filenames(
        config["input-source"], config["input-patterns"]
    )

    for i in trange(filenames.__len__()):
        filename = filenames[i]
        filepath = os.path.basename(filename)

        image = autovrai.load_image(filename)

        if config["precision-mode"] == "dynamic":
            raise ValueError("Dynamic precision mode is not yet implemented, sorry...")

        if config["precision-type"] == "factor":
            set_precision(
                model,
                image.width * config["precision-width"],
                image.height * config["precision-height"],
            )
        elif config["precision-type"] == "pixels":
            set_precision(model, config["precision-width"], config["precision-height"])
        else:
            raise ValueError("Invalid precision-type")

        depth: np.ndarray = model.infer_pil(image, output_type="numpy")

        left, right = autovrai.stereo_eyes(image, depth, config["stereo-intensity"])

        if config["output-stereo"] != "":
            stereo = autovrai.combine_stereo(left, right)
            stereo.save(os.path.join(config["output-stereo"], filepath))
        if config["output-padded"] != "":
            padded = autovrai.combine_padded(
                left,
                right,
                int(round(image.width * 1.5)),
                int(round(image.height * 1.5)),
            )
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

    return []
