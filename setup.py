#!/usr/bin/env python

import re
from os import path
from setuptools import setup, find_packages

__folder__ = path.dirname(__file__)

with open(path.join(__folder__, "README.md")) as ld_file:
    long_description = ld_file.read()
    ld_file.flush()

with open(path.join(__folder__, "CTFDump.py")) as lib_file:
    r = re.search(r"__version__\s+=\s+(?P<q>[\"'])(?P<ver>\d+(?:\.\d+)*)(?P=q)", lib_file.read())
    version = r.group('ver')

with open(path.join(__folder__, "requirements.txt")) as req_file:
    install_requires = req_file.read()

setup(
    name="CTFDump",
    version=version,
    description="CTFd Dump - When you want to have an offline copy of a CTF.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="RealGame (Tomer Zait)",
    author_email="realgam3@gmail.com",
    packages=find_packages(exclude=["examples", "tests"]),
    py_modules=["CTFDump"],
    entry_points={
        "console_scripts": [
            "ctf-dump = CTFDump:main",
        ]
    },
    install_requires=install_requires,
    license="GPLv3",
    platforms="any",
    url="https://github.com/mosheDO/CTFDump",
    classifiers=[
        "License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
        "Development Status :: 5 - Production/Stable",
        "Environment :: Console",
        "Intended Audience :: Science/Research",
        "Natural Language :: English",
        "Operating System :: MacOS :: MacOS X",
        "Operating System :: Microsoft :: Windows",
        "Operating System :: POSIX :: Linux",
        "Programming Language :: Python :: 3",
        "Topic :: Security",
        "Topic :: Internet",
        "Topic :: Internet :: WWW/HTTP",
    ]
)
