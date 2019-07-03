#!/usr/bin/env python3
# author: Kevin T. Lee<hello@lidengju.com>
# description: the setuptools control

from setuptools import setup


with open("README.md", "rb") as f:
    long_descr = f.read().decode("utf-8")


setup(
    name="dj-beat",
    packages=["djbeat"],
    entry_points={
        "console_scripts": ['djbeat = djbeat.djbeat:main']
    },
    version='0.4.9',
    description="A simple CLI tool for generating beat marks of music for FCPX and PRE",
    license="MIT",
    install_requires=[
        'Cython',
        'numpy',
        'tqdm',
        'madmom',
        'librosa',
        'pyfiglet',
        'urllib3'
    ],
    # long_description=long_descr,
    include_package_data=True,
    author="Kevin T. Lee",
    author_email="hello@lidengju.com",
    url="http://lidengju.com/dj-beat",
)
