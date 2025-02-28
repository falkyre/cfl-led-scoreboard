#!/bin/bash

# Make script work regardless of where it is run from
DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"
cd "${DIR}/.." || exit

echo "$(tput setaf 6)Installing required dependencies. This may take some time (10-20 minutes-ish)...$(tput setaf 9)"

pip3 install --upgrade pip wheel setuptools

#Install all requirements using the requirements.txt filler
pip3 install -r requirements.txt

# Pull submodule and ignore changes from script
git submodule update --init --recursive
git config submodule.matrix.ignore all

echo "$(tput setaf 4)Running rgbmatrix installation...$(tput setaf 9)"

# Recompile the cpp files to build library with newest cython.  See https://github.com/hzeller/rpi-rgb-led-matrix/issues/1298

cd submodules/matrix/bindings/python/rgbmatrix/ || exit

python3 -m pip install --no-cache-dir cython
python3 -m cython -2 --cplus *.pyx

cd ../../../ || exit

make build-python PYTHON="$(command -v python3)"
sudo make install-python PYTHON="$(command -v python3)"

cd ../../../ || exit

git reset --hard
git fetch origin --prune
git pull

make
echo "If you didn't see any errors above, everything should be installed!"
echo "$(tput bold)$(tput smso)$(tput setaf 2)Installation complete!$(tput sgr0) Play around with the examples in cfl-led-scoreboard/submodules/matrix/bindings/python/samples to make sure your matrix is working."
