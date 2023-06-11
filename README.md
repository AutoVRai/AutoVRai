# AutoVR.ai

AI-powered toolkit for converting 2D media into immersive VR using local hardware

---

## Installation

This might be a bit rough for now, but I'll try to make it easier to install in the future. Development was done with python version `3.10.11`.

### Requirements

These should be handled by `requirements.txt` or `setup.py` but I'm not sure if I'm doing it right. In the meantime, you can try:

```bash
pip install -r requirements.txt
```

or manually:

```bash
pip install gradio jsonschema numba numpy opencv-python Pillow torch torchvision tqdm
```

### Model Files

Right now you'll need to provide the model files manually. An automatic download will be added in the future.

1. Create a directory inside the project root called `checkpoints`
2. Download the model file or files you'd like to use into the `checkpoints` directory:
  - **zoedepth_nk** - https://github.com/isl-org/ZoeDepth/releases/download/v1.0/ZoeD_M12_NK.pt
  - **zoedepth_n** - https://github.com/isl-org/ZoeDepth/releases/download/v1.0/ZoeD_M12_N.pt
  - **zoedepth_k** - https://github.com/isl-org/ZoeDepth/releases/download/v1.0/ZoeD_M12_K.pt

Alternatively, you can create a symlink to the model files in the `checkpoints` directory or create a symlink named `checkpoints` to a directory that has the model files.

## Usage Examples

Launching the CLI using all defaults:
```bash
python autovrai
```

Launching the GUI using all defaults:
```bash
python autovrai --gui
```

Getting the help information:
```bash
python autovrai --help
```

Launching the CLI with custom settings:
```bash
python autovrai --input-source 'c:\Users\Someone\Somewhere' --device-name 'cpu'
```

Launching the CLI with a custom config file (needs created):
```bash
python autovrai --config-file 'configs/some-config.json'
```

## Configuration and Defaults

The full set of default values can be seen in `configs/__defaults__.json`, but that file should not be changed. Instead, you can create a new config file and override the values you want to change. The defaults get loaded automatically, followed by a custom config file if provided, then any parameters provided when launching will override those values. This behavior works the same for the CLI mode and GUI mode.

The resulting `config` object is used throughout the program to determine how to run. It is re-validated against the `configs/__schema__.json` file representing a `jsonschema` definition. That definition will also help provide some documentation on what each parameter does, acceptable values, and other information. Be sure to include the `$schema` element in any custom config files similar to how it appears in `__defaults__.json`.

