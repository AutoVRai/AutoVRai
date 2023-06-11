from setuptools import setup, find_packages

setup(
    name="AutoVRai",
    version="0.5",
    description="AI-powered toolkit for converting 2D media into immersive VR using local hardware",
    author="Brian Jorden",
    license="MIT",
    url="https://github.com/AutoVRai/AutoVRai",
    packages=find_packages(),
    entry_points={
        "console_scripts": [
            "AutoVRai-cli = autovrai.cli:main",
            "AutoVRai-web = autovrai.web:main",
            "AutoVRai-deo = autovrai.deo:main",
        ],
    },
    python_requires=">=3.10",
    install_requires=[
        # let me know if i've missed anything
        "gradio",
        "jsonschema",
        "numba",
        "numpy",
        "opencv-python",
        "Pillow",
        "scipy",
        "torch",
        "torchvision",
        "tqdm",
    ],
)
