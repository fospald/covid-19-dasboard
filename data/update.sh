#!/bin/bash

git submodule update --recursive --remote
git submodule update --recursive
git pull --recurse-submodules

python3 rki_pull.py
python3 build.py

