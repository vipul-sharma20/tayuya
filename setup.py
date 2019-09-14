import setuptools


with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="tayuya",
    version="0.0.3",
    author="Vipul Sharma",
    author_email="vipul.sharma20@gmail.com",
    description="MIDI to guitar tabs generator",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/vipul-sharma20/tayuya",
    packages=setuptools.find_packages(),
    install_requires=["mido", "music21"],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
)
