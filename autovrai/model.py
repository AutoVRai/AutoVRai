from ZoeDepth.zoedepth.models.builder import build_model, DepthModel
from ZoeDepth.zoedepth.utils.config import get_config
from ZoeDepth.zoedepth.utils.misc import colorize, save_raw_16bit


def model_loader(model_name, device_name):
    if model_name.lower().startswith('zoedepth'):
        return load_zoedepth(model_name, device_name)

    raise ValueError("Invalid model name")


def load_zoedepth(model_name, device_name):
    if model_name == "zoedepth_nk":
        conf = get_config("zoedepth_nk", "infer")
    elif model_name == "zoedepth_n":
        conf = get_config("zoedepth", "infer")
    elif model_name == "zoedepth_k":
        conf = get_config("zoedepth", "infer", config_version="kitti")
    else:
        raise ValueError("Invalid model name")

    model = build_model(conf)
    model.to(device_name)

    return model
