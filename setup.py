from setuptools import setup, find_packages

setup(
    name="AutoVRai",
    version="0.4",
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
        # there are several, not sure exactly what yet, sorry...
    ],
)
