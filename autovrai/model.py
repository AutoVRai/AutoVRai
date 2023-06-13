import gc
import torch
import warnings

import autovrai


# gets rid of a future deprecation warning that would require changing the ZoeDepth code
warnings.filterwarnings(
    "ignore", category=UserWarning, module="torch.functional", lineno=504
)

# treating the model as a singleton, so we can unload it when we need to
MODEL = None

# these are the details of the model that is currently loaded so we know if we need to
# unload and reload it, or if we can just use the version already loaded
NAME = None
DEVICE = None
WIDTH = None
HEIGHT = None


def model_loader(config, base_width: int, base_height: int, factor: float):
    device_name = config["device-name"].lower()
    device_name = "cuda" if device_name == "gpu" else device_name

    # handle variations of the model name, but make it uniform and ready for torch hub
    model_name = config["model-name"].lower()
    if model_name in ["zoedepth_nk", "zoed_m12_nk", "zoed_nk"]:
        model_name = "ZoeD_NK"
    elif model_name in ["zoedepth_n", "zoed_m12_n", "zoed_n"]:
        model_name = "ZoeD_N"
    elif model_name in ["zoedepth_k", "zoed_m12_k", "zoed_k"]:
        model_name = "ZoeD_K"
    else:
        raise ValueError("Invalid model name")

    # used to tell the model what "precision" to operate at, in a prior version the
    # approach was to set the model resizer's width and height before processing each
    # image, but found that there were memory leaks related to that approach. now the
    # model is built once, and the resizer is set once, so the model needs to be
    # unloaded and reloaded if the precision to process at changes. note, the height
    # and width look swapped here because of how the model uses this internally
    width = int(round(base_width * factor))
    height = int(round(base_height * factor))
    img_size = [height, width]

    # if the model is already loaded, and the details are the same, just return it
    global MODEL, NAME, DEVICE, WIDTH, HEIGHT
    if MODEL is not None:
        if (
            NAME == model_name
            and DEVICE == device_name
            and WIDTH == width
            and HEIGHT == height
        ):
            return MODEL
        else:
            MODEL = model_unloader(MODEL)

    print(
        "--- AutoVR.ai ---",
        f"Loading (model-name: {model_name}) onto (device-name: {device_name})",
    )
    print(
        "--- AutoVR.ai ---",
        f"Using the precision of (width: {width}) and (height: {height})",
    )
    print(
        "--- AutoVR.ai ---",
        f"Based on "
        f"(base-width: {base_width}) "
        f"and (base-height: {base_height}) "
        f"and (factor: {factor})",
    )

    # we will print out our own model information instead
    with autovrai.suppress_output():
        MODEL = torch.hub.load(
            "isl-org/ZoeDepth",
            model_name,
            pretrained=True,
            img_size=img_size,
        )
        MODEL.to(device_name)
        MODEL.eval()

    NAME = model_name
    DEVICE = device_name
    WIDTH = width
    HEIGHT = height

    cleanup()
    return MODEL


def model_unloader(model):
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
    if cuda_available and device_name != "cpu":
        with torch.cuda.device(DEVICE):
            torch.cuda.empty_cache()
            torch.cuda.ipc_collect()
