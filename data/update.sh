#!/bin/bash

git pull --recurse-submodules
python3 rki_pull.py
python3 build.py

