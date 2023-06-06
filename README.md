# AutoVRai (new)
AI-powered toolkit for converting 2D media into immersive VR using local hardware

## Installation

ln -s ~/Models/ZoeDepth checkpoints
https://github.com/isl-org/ZoeDepth/releases/tag/v1.0


---
---
---


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


---
---
---


# AutoVRai (chatgpt)

AutoVRai is an open-source project that leverages AI to convert and enhance regular images and videos into Flat 3D or VR180. It can be run entirely on local hardware, with a modern mid-range gaming PC serving as a typical setup.

## Features
- Automated conversion with minimal user input
- Default and user-customizable configurations via JSON files
- Multiple modes of interaction including CLI, a local network web app, and a special mode for DeoVR
- In future, native app for Oculus Quest for immersive VR interaction

The primary mode of interaction is via a simple web interface accessible on the local network, but a CLI is also provided for automation and scripting. A special mode for DeoVR allows streaming of VR videos and images to a VR headset.

This project is written in Python and planned for future Docker containerization. It's the perfect project to dive into for both open-source enthusiasts and AI/ML beginners. For a detailed description of the project structure, please refer to the 'Project Structure' section.



---
---
---

# AutoVRai (original)

### Depth Map Information
- https://github.com/thygate/stable-diffusion-webui-depthmap-script/discussions/45
- https://github.com/thygate/stable-diffusion-webui-depthmap-script/pull/51
- https://github.com/thygate/stable-diffusion-webui-depthmap-script/pull/56

### Related Packages
- https://github.com/thygate/stable-diffusion-webui-depthmap-script
- https://github.com/isl-org/ZoeDepth
- https://github.com/m5823779/stereo-image-generation


### VR Specific Information
- https://gist.github.com/nickkraakman/e351f3c917ab1991b7c9339e10578049
- https://headjack.io/knowledge-base/best-video-resolution-for-oculus-quest/
- https://creator.oculus.com/media-studio/documentation/video-spec/
- https://creator.oculus.com/media-studio/documentation/rectangular-video-spec/
- https://github.com/google/spatial-media


## Potential Competitors
- https://headjack.io/knowledge-base/best-video-resolution-for-oculus-quest/
- https://www.owl3d.com/


## Video Enhancements

### RIFE (smoother video?)
- https://www.svp-team.com/wiki/RIFE_AI_interpolation


## NeRF Crazyness
- https://twitter.com/soundsof_echoes/status/1620793294883262465
- https://twitter.com/soundsof_echoes/status/1621462119102177283

### text2nerf
- https://twitter.com/_akhaliq/status/1660451122669322240
- https://huggingface.co/papers/2305.11588

### instant-ngp
- https://github.com/NVlabs/instant-ngp#building-instant-ngp-windows--linux


## Web Based VR Viewing

### vrEmbed
- https://github.com/bhautikj/vrEmbed
- https://lisa-wolfgang.github.io/vrEmbed/docs/example_stereo.html

### vue-vr
- https://github.com/mudin/vue-vr

### React360
- https://github.com/facebookarchive/react-360



## Performance
https://github.com/nv-legate/cunumeric
https://catalog.ngc.nvidia.com/orgs/nvidia/containers/pytorch#cid=dl13_so-yout_en-us
https://developer.nvidia.com/tensorrt
https://cupy.dev/


## Reference

### Stable Diffusion Stuff
https://rentry.org/sd-mashup







