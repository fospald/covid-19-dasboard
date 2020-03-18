#!/bin/bash

git pull --recurse-submodules

cd COVID-19
git checkout master
git pull
cd ..

cd COVID-19-Germany
git checkout master
git pull
cd ..

python3 rki_pull.py
python3 build.py

