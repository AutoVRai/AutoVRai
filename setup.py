from setuptools import setup, find_packages

setup(
    name="AutoVRai",
    version="0.7",
    description="AI-powered toolkit for converting 2D media into immersive VR using local hardware",
    author="Brian Jorden",
    license="MIT",
    url="https://github.com/AutoVRai/AutoVRai",
    packages=find_packages(),
    entry_points={
        "console_scripts": [],
    },
    python_requires=">=3.10",
    install_requires=[
        # let me know if i've missed anything
        "gradio",
        "jsonschema",
        "matplotlib",
        "numba",
        "numpy",
        "opencv-python",
        "Pillow",
        "scipy",
        "timm==0.6.13",
        "torch",
        "torchvision",
        "tqdm",
    ],
)
