#!/usr/bin/env python3

from setuptools import find_packages, setup

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

with open("requirements.txt", "r", encoding="utf-8") as f:
    requirements = f.read().splitlines()

setup(
    name="flaccid",
    version="0.1.0",
    author="FLACCID Team",
    author_email="info@flaccid.example.com",
    description="A CLI toolkit for downloading and tagging FLAC files",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/your-repo/flaccid",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    classifiers=[
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.10",
    install_requires=requirements,
    entry_points={
        "console_scripts": [
            "fla=flaccid.cli.__init__:main",
        ],
    },
)
