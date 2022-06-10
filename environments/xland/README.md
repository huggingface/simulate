# XLand-like environment

Procedurally generated environments inspired by [XLand](https://arxiv.org/abs/2107.12808) from Deepmind.

<img src="benchmark/media/maps.gif" width="500">

For now, we are building the procedural generation using [Wave Function Collapse](https://github.com/mxgmn/WaveFunctionCollapse) (WFC), and we use an external dependency called [fast-wfc](https://github.com/math-fehr/fast-wfc), which contains a really fast implementation of WFC in C++.

## Installation

First, install the Wave Function Collapse C++ library (you will need cmake which can be installed with `sudo apt install cmake` (Linux) or `brew install cmake` (MacOS)):

```
git clone https://github.com/math-fehr/fast-wfc && cd fast-wfc && cmake . && sudo make install
```

Troubleshooting w.r.t. to C++ external library installation: 

* When installing an external library in C++, you might need to create the links to `usr/local/lib`, and other usual paths for C++ library installation. The installation of this particular external library doesn't update the links, so you might need to run `sudo ldconfig` in Linux.

* On MacOS, you might face the same issue. If that's the case, please follow this next extra step: for a temporary solution, run `export DYLD_LIBRARY_PATH=/usr/local/lib:$DYLD_LIBRARY_PATH` on the terminal you will be using to run the code. If you want changes to be persistent, add the export command on your profile file (e.g. `~/.zprofile`). It's possible to make it work without this extra step (but not as easy as in Linux, unfortunately), however we are still working on identifying the exact solution (one non-ideal solution is to install another C++ library that updates the links in MacOS).

Then create a virtual env, activate it, and then install `simenv`:

```
cd .. && git clone https://github.com/huggingface/simenv.git
cd simenv
pip install -e ".[dev]"
```

Then install the `xland` package:

```
cd environments/xland
pip install -e ".[dev]"
```

So far, the environment was not tested on Windows.

### Style

Before you merge a PR, fix the style (we use `isort` + `black`)
```
make style
```

## Basic Usage

A minimalistic example to generate from an example map:

```
from xland import gen_setup, generate_env
from xland.utils import create_2d_map

# Generate initial tiles and structure to save maps and etc
gen_setup()

# Create example map from csv file on examples
create_2d_map(name="example_map_01")

# Sample from example map and show interactive mode
generate_env(width=8, height=8, sample_from="example_map_01", show=True)
```

Other scripts might be found in the folder `scripts`. The map that is used as example is in CSV format for human readability inside the `benchmark/examples`.