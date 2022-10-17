<p align="center">
    <br>
    <img src="docs/source/assets/simulate_library.png" width="400"/>
    <br>
</p>
<p align="center">
    <a href="https://github.com/huggingface/simulate/blob/main/LICENSE">
        <img alt="GitHub" src="https://img.shields.io/github/license/huggingface/datasets.svg?color=blue">
    </a>
    <a href="https://github.com/huggingface/simulate/releases">
        <img alt="GitHub release" src="https://img.shields.io/github/release/huggingface/diffusers.svg">
    </a>
    <a href="CODE_OF_CONDUCT.md"> 
        <img alt="Contributor Covenant" src="https://img.shields.io/badge/Contributor%20Covenant-2.0-4baaaa.svg">
    </a>
</p>

# Simulate

Simulate is a library for easily creating and sharing simulation environments for intelligent agents (e.g. reinforcement learning) or synthetic data generation.

## Install

Install Simulate (preferentially in a virtual environment) with a simple `pip install simulate`

### Install for contribution (from [CONTRIBUTING.md](CONTRIBUTING.md))

Create a virtual env and then install the code style/quality tools as well as the code base locally
```
pip install --upgrade simulate
```
Before you merge a PR, fix the style (we use `isort` + `black`)
```
make style
```

## Quick tour

Simulate's API is inspired by the great [Kubric's API](https://github.com/google-research/kubric).
The user create a `Scene` and add `Assets` in it (objects, cameras, lights etc).

Once the scene is created, you can save and share it as a file. This is a gIFT file, aka a JSON file with associated resources.

You can also render the scene or do simulations using one of the backend rendering/simulation engines (at the moment Unity, Blender and Godot).

The saving/sharing format is engine agnostic and using a graphic industry standard.

Let's do a quick exploration together.  

```
import simulate as sm

scene = sm.Scene()
```

### Project Structure

The Python API is located in src/simulate. It allows creation and loading of scenes, and sending commands to the backend.

We provide several backends to render and/or run the scene.
The default backend requires no specific installation and is based on [pyvista](https://docs.pyvista.org/user-guide/index.html). It allows one to quick render/explored scene but doesn't handle physics simulation.
To allow physic simulations, the Unity backend can for instance be used by setting `engine="unity"` (and soon the Godot and Blender Engines backend as well). A Unity build will be automatically downloaded (if not already) and spawed to run simulations. Alternatively, one can download and use the Unity editor themself, which must then be opened with Unity version 2021.3.2f1.

### Loading a scene from the Hub or a local file

Loading a scene from a local file or the Hub is done with `Scene.create_from()`, saving locally or pushing to the Hub with `scene.save()` or `scene.push_to_hub()`:

```
from simulate import Scene

scene = Scene.create_from('tests/test_assets/fixtures/Box.gltf')  # either local (priority) or on the Hub with full path to file
scene = Scene.create_from('simulate-tests/Box/glTF/Box.gltf', is_local=False)  # Set priority to the Hub file

scene.save('local_dir/file.gltf')  # Save to a local file
scene.push_to_hub('simulate-tests/Debug/glTF/Box.gltf')  # Save to the Hub - use a token if necessary

scene.show()
```
<p align="center">
    <br>
    <img src="https://user-images.githubusercontent.com/10695622/191554717-acba4764-a4f4-4609-834a-39ddb50b844a.png" width="400"/>
    <br>
<p>

### Creating a Scene and adding/managing Objects in the scene

Basic example of creating a scene with a plane and a sphere above it:
```
import simulate as sm

scene = sm.Scene()
scene += sm.Plane() + sm.Sphere(position=[0, 1, 0], radius=0.2)

>>> scene
>>> Scene(dimensionality=3, engine='PyVistaEngine')
>>> └── plane_01 (Plane - Mesh: 121 points, 100 cells)
>>>     └── sphere_02 (Sphere - Mesh: 842 points, 870 cells)

scene.show()
```

An object (as well as the Scene) is just a node in a tree provided with optional mesh (under the hood created/stored/edited as a [`pyvista.PolyData`](https://docs.pyvista.org/api/core/_autosummary/pyvista.PolyData.html#pyvista-polydata) or [`pyvista.MultiBlock`](https://docs.pyvista.org/api/core/_autosummary/pyvista.MultiBlock.html#pyvista-multiblock) objects) and material and/or light, camera, agents special objects.

The following objects creation helpers are currently provided:
- `Object3D` any object with a mesh and/or material
- `Plane`
- `Sphere`
- `Capsule`
- `Cylinder`
- `Box`
- `Cone`
- `Line`
- `MultipleLines`
- `Tube`
- `Polygon`
- `Ring`
- `Text3D`
- `Triangle`
- `Rectangle`
- `Circle`
- `StructuredGrid`
- ... (see the doc)

Many of these objects can be visualized by running the following [example](https://github.com/huggingface/simulate/tree/main/examples/objects.py):
```
python examples/basic/objects.py
```
<p align="center">
    <br>
    <img src="https://user-images.githubusercontent.com/10695622/191562825-49d4c692-a1ed-44e9-bdb9-da5f0bfb9828.png" width="400"/>
    <br>
<p>

### Objects are organized in a tree structure

Adding/removing objects:
- Using the addition (`+`) operator (or alternatively the method `.add(object)`) will add an object as a child of a previous object.
- Objects can be removed with the subtraction (`-`) operator or the `.remove(object)` command.
- Several objects can be added at once by adding a list/tuple to the scene.
- The whole scene can be cleared with `.clear()`.
- To add a nested object, just add it to the object under which it should be nested, e.g. `scene.sphere += sphere_child`.

Accessing objects:
- Objects can be directly accessed as attributes of their parents using their names (given with  `name` attribute at creation or automatically generated from the class name + creation counter).
- Objects can also be accessed from their names with `.get_node(name)`.
- The names of the object are enforced to be unique (on save/show).
- Various `tree_*` attributes are available on any node to quickly navegate or list part of the tree of nodes.

Here are a couple of examples of manipulations:

```
# Add two copy of the sphere to the scene as children of the root node (using list will add all objects on the same level)
# Using `.copy()` will create a copy of an object (the copy doesn't have any parent or children)
scene += [scene.plane_01.sphere_02.copy(), scene.plane_01.sphere_02.copy()]

>>> scene
>>> Scene(dimensionality=3, engine='pyvista')
>>> ├── plane_01 (Plane - Mesh: 121 points, 100 cells)
>>> │   └── sphere_02 (Sphere - Mesh: 842 points, 870 cells)
>>> ├── sphere_03 (Sphere - Mesh: 842 points, 870 cells)
>>> └── sphere_04 (Sphere - Mesh: 842 points, 870 cells)

# Remove the last added sphere
>>> scene.remove(scene.sphere_04)
>>> Scene(dimensionality=3, engine='pyvista')
>>> ├── plane_01 (Plane - Mesh: 121 points, 100 cells)
>>> │   └── sphere_02 (Sphere - Mesh: 842 points, 870 cells)
>>> └── sphere_03 (Sphere - Mesh: 842 points, 870 cells)
```

### Editing and moving objects

Objects can be easily translated, rotated, scaled

Here are a couple of examples:
```
# Let's translate our floor (with the first sphere, it's child)
scene.plane_01.translate_x(1)

# Let's scale the second sphere uniformly
scene.sphere_03.scale(0.1)

# Inspect the current position and scaling values
print(scene.plane_01.position)
>>> array([1., 0., 0.])
print(scene.sphere_03.scaling)
>>> array([0.1, 0.1, 0.1])

# We can also translate from a vector and rotate from a quaternion or along the various axis
```

Editing objects:
- mesh of the object can be edited with all the manipulation operator provided by [pyvista](https://docs.pyvista.org/user-guide/index.html)

## Visualization engine

A default visualization engine is provided with the vtk backend of [`pyvista`](https://docs.pyvista.org/user-guide/index.html).

Starting the visualization engine can be done simply with `.show()`.
```
scene.show()
```

You can find bridges to other rendering/simulation engines in the `integrations` directory.

## Tips

If you are running on GCP, remember not to install `pyvistaqt`, and if you did so, uninstall it in your environment, since QT doesn't work well on GCP.

## Citation
```bibtex
@misc{simulate,
  author = {Thomas Wolf, Edward Beeching, Carl Cochet, Dylan Ebert, Alicia Machado, Nathan Lambert, Clément Romac},
  title = {Simulate},
  year = {2022},
  publisher = {GitHub},
  journal = {GitHub repository},
  howpublished = {\url{https://github.com/huggingface/simulate}}
}
```
