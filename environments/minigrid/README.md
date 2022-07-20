# Minigrid-like environment

Minimalistic gridworld environment inspired by [Minigrid](https://github.com/Farama-Foundation/gym-minigrid)

## Installation
Create a virtual env, activate it, and then install `simenv`:

```
cd .. && git clone https://github.com/huggingface/simenv.git
cd simenv
pip install -e ".[dev]"
```

Then install the `minigrid` package:

```
cd environments/minigrid
pip install -e ".[dev]"
```

And it's done!

### Style

Before you merge a PR, fix the style (we use `isort` + `black`)
```
make style
```

## Basic Usage

