# simenv
Creating and sharing simulation environments for RL and synthetic data generation

To install and contribute (from the CONTRIBUTING.md doc)

Create a virtual env and then install the code style/quality tools as well as the code base locally
```
pip install -e ".[dev]"
```
Before you merge a PR, fix the style (we use `isort` + `black`)
```
make style
```
