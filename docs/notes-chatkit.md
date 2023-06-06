# AutoVRai (chatkit)

AutoVRai is an open-source project that automates the conversion and enhancement of regular images and videos into Flat 3D or VR180. It is primarily written in Python and leverages core concepts from several other projects, tools, and AIs.

## Modes of Operation

AutoVRai can be used in the following modes:

- **Web**: Launches a Gradio web app for a simple local network interface to select images or videos to convert.
- **App**: (Future version) A native Oculus Quest application for a fully immersed VR experience.
- **CLI**: A command-line interface for automation and scripting.
- **Deo**: Generates a JSON configuration file for the DeoVR app and optionally launches a local web server for streaming VR content.

## Getting Started

1. Clone the repository.
2. Install the required dependencies.
3. Run AutoVRai in the desired mode.

For detailed usage instructions, please refer to the [Usage](#usage) section.

## Usage

### Web Mode

To launch the Gradio web app:

```
python -m auto_vrai.web
```

### CLI Mode

To use the command-line interface:

```
python -m auto_vrai.cli [config_file] [options]
```

### Deo Mode

To generate the DeoVR configuration file and launch the local web server:

```
python -m auto_vrai.deo [directory] [options]
```
