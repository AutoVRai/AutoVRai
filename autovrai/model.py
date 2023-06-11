import gc
import torch
import warnings

from ZoeDepth.zoedepth.models.builder import build_model, DepthModel
from ZoeDepth.zoedepth.utils.config import get_config
from ZoeDepth.zoedepth.utils.misc import colorize, save_raw_16bit

import autovrai


# gets rid of a future deprecation warning that would require changing the ZoeDepth code
warnings.filterwarnings(
    "ignore", category=UserWarning, module="torch.functional", lineno=504
)

# defining these so they can be imported by __init__
ZoeDepth_DepthModel = DepthModel
ZoeDepth_colorize = colorize
ZoeDepth_save_raw_16bit = save_raw_16bit

# treating the model as a singleton, so we can unload it when we need to
MODEL = None

# these are the details of the model that is currently loaded so we know if we need to
# unload and reload it, or if we can just use the version already loaded
NAME = None
DEVICE = None
WIDTH = None
HEIGHT = None


def model_loader(config, base_width: int, base_height: int, factor: float):
    model_name = config["model-name"].lower()
    device_name = config["device-name"].lower()

    # these are the calculated dimensions for the model to use
    width = int(round(base_width * factor))
    height = int(round(base_height * factor))

    # if the model is already loaded, and the details are the same, just return it
    global MODEL, NAME, DEVICE, WIDTH, HEIGHT
    if MODEL is not None:
        if (
            NAME == model_name
            and DEVICE == device_name
            and WIDTH == width
            and HEIGHT == height
        ):
            cleanup()
            return MODEL
        else:
            MODEL = model_unloader(MODEL)

    # make sure we load the right model and settings
    if model_name == "zoedepth_nk":
        conf = get_config("zoedepth_nk", "infer")
    elif model_name == "zoedepth_n":
        conf = get_config("zoedepth", "infer")
    elif model_name == "zoedepth_k":
        conf = get_config("zoedepth", "infer", config_version="kitti")
    else:
        raise ValueError("Invalid model name")

    # this tells the model what "precision" to operate at, in a prior version the
    # approach was to set the model resizer's width and height before processing each
    # image, but found that there were memory leaks related to that approach. now the
    # model is built once, and the resizer is set once, so the model needs to be
    # unloaded and reloaded if the precision to process at changes. note, the height
    # and width look swapped here because of how the model uses this internally
    conf.img_size = [height, width]

    print(
        "--- AutoVR.ai ---",
        f"Loading (model-name: {model_name}) "
        f"onto (device-name: {device_name}) "
        f"using the precision "
        f"of (width: {width}) "
        f"and (height: {height})",
    )

    # we will print out our own model information instead
    with autovrai.suppress_output():
        MODEL = build_model(conf)
        MODEL.to(device_name).eval()

    NAME = model_name
    DEVICE = device_name
    WIDTH = width
    HEIGHT = height

    cleanup()
    return MODEL


def model_unloader(model: ZoeDepth_DepthModel):
    global MODEL, NAME, DEVICE, WIDTH, HEIGHT

    del model
    del MODEL

    MODEL = None
    NAME = None
    DEVICE = None
    WIDTH = None
    HEIGHT = None

    cleanup()
    return None


def cleanup():
    cuda_available = torch.cuda.is_available()

    global DEVICE
    device_name = DEVICE
    if device_name == None:
        if cuda_available:
            device_name = "cuda"
        else:
            device_name = "cpu"

    gc.collect()
    if cuda_available:
        with torch.cuda.device(DEVICE):
            torch.cuda.empty_cache()
            torch.cuda.ipc_collect()
