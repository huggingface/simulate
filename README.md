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

## Project Structure

The Python API is located in src/simenv. It allows creation and loading of scenes, and sending commands to the backend.

The backend, currently just Unity, is located in integrations/Unity. This is currently a Unity editor project, which must be opened in Unity 2021.3.2f1. In the future, this will be built as an executable, and spawned by the Python API.

## Creating a Scene and adding/managing Objects in the scene

Basic example of creating a scene with a plane and a sphere above it:
```
import simenv as sm

scene = sm.Scene()
scene += sm.Plane() + sm.Sphere(position=(0, 1, 0), radius=0.2)

print(scene)
>>> Scene(dimensionality=3, engine='PyVistaEngine')
>>> └── plane_01 (Plane - Mesh: 121 points, 100 cells)
>>>     └── sphere_02 (Sphere - Mesh: 842 points, 870 cells)

scene.show()
```

An object (as well as the Scene) is just a node in a tree provided with optional mesh (as `pyvista.PolyData` structure) and material and/or light, camera, agents special objects.

The following objects creation helpers are currently provided:
- `Object3D` any object with a `pyvista.PolyData` mesh and/or material
- `Plane`
- `Sphere`
- `Capsule`
- `Cylinder`
- `Cube`
- `Cone`
- `Line`
- `MultipleLines`
- `Tube`
- `Polygon`
- `Disc`
- `Text3D`
- `Triangle`
- `Rectangle`
- `Circle`
- `StructuredGrid`

### Objects are organized in a tree structure

Adding/removing objects:
- Using the addition (`+`) operator (or alternatively the method `.add(object)`) will add an object as a child of a previous object.
- Objects can be removed with the substraction (`-`) operator or the `.remove(object)` command.
- The whole scene can be cleared with `.clear()`.

Accessing objects:
- Objects can be directly accessed as attributes of their parents using their names (given with  `name` attribute at creation or automatically generated from the class name + creation counter).
- Objects can also be accessed from their names with `.get(name)` or by naviguating in the tree using the various `tree_*` attributes available on any node.

Here are a couple of examples of manipulations:

```
# Add two copy of the sphere to the scene as children of the root node (using list will add all objects on the same level)
# Using `.copy()` will create a copy of an object (the copy doesn't have any parent or children)
scene += [scene.plane_01.sphere_02.copy(), scene.plane_01.sphere_02.copy()]

print(scene)
>>> Scene(dimensionality=3, engine='PyVistaEngine')
>>> ├── plane_01 (Plane - Mesh: 121 points, 100 cells)
>>> │   └── sphere_02 (Sphere - Mesh: 842 points, 870 cells)
>>> ├── sphere_03 (Sphere - Mesh: 842 points, 870 cells)
>>> └── sphere_04 (Sphere - Mesh: 842 points, 870 cells)

# Remove the last added sphere
scene.remove(scene.sphere_04)
>>> Scene(dimensionality=3, engine='PyVistaEngine')
>>> ├── plane_01 (Plane - Mesh: 121 points, 100 cells)
>>> │   └── sphere_02 (Sphere - Mesh: 842 points, 870 cells)
>>> └── sphere_03 (Sphere - Mesh: 842 points, 870 cells)
```

### Objects can be translated, rotated, scaled
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

### Visualization engine

A default vizualization engine is provide with the vtk backend of `pyvista`.

Starting the vizualization engine can be done simply with `.show()`.
```
scene.show()
```

## Using with Unity as engine

### Install with the Unity editor

Currently we use Unity version `2021.3.2f1` as the development version.

To install and run the project in Unity:
- First install Unity `2021.3.2f1` using the Unity Hub if you don't have it
- From the Unity Hub, open the project at `./integrations/Unity/simenv-unity`
- Open the Sample Scene or create a new scene with an empty GameObject with a `Client.cs` component attached

### Run with the Unity engine

1. If it's not already opened, open the Unity project with Scene with a GameObject with a `Client.cs` component attached.
2. Create the `simenv` scene with a `'Unity'` engine, for example:
```
import simenv as sm

scene = sm.Scene(engine="Unity")
scene += sm.Sphere()
scene.render()
```
3. Run the python script. It should print "Waiting for connection...", meaning that it has spawned a websocket server, and is waiting for a connection from the Unity client.
4. Press Play in Unity. It should connect to the Python client, then display a basic Sphere. The python script should finish execution.

### Creating Custom Functionality

Communication with the backend is through JSON messages over a socket connection. A socket command has the following format:
```
{
    "type": "MyCommand",
    "contents": json.dumps({
        "message": "hello from python API"
    })
}
```
The `type` and `contents` dict is a wrapper around each command. The internal contents of the command are an embedded JSON string in `contents`.

The above example will only work if `MyCommand` is implemented in the backend. To implement this in the backend, add the following script in the Unity project:
```
using UnityEngine.Events;
using SimEnv;

public class MyCommand : Command {
    public string message;
    
    public override void Execute(UnityAction<string> callback) {
        Debug.Log(message);
        callback("ack");
    }
}
```

Simply adding the script to the project should be sufficient to make it work. Any public fields defined in a `Command` can be passed through your `contents` JSON. Only simple types (i.e. `int`, `float`, `string`) and arrays are supported, not Lists, Vector3, etc., since it uses Unity's built-in JSON serialization. You need to serialize/deserialize these yourself.

### Collider Extension

The HF_collider extension is based loosely on the PANDA3D_physics_collision_shapes extension: https://github.com/Moguri/glTF/tree/panda3d_physics_collision_shapes/extensions/2.0/Vendor/PANDA3D_collision_shapes

This extension is defined at the node-level. For example, a node with a box collider:
```
{
    "extensions": {
        "HF_collider": {
            {
                "type": "BOX",
                "boundingBox": [
                    0.5,
                    0.5,
                    0.5
                ]
            }
        }
    }
}
```

This currently only supports Box, Sphere, and Capsule colliders (the Unity/PhysX colliders).

Differences from the PANDA3D extension:
- Properties `group` and `mask` are removed, since layer interactions are defined engine-wide, not per-object, in Unity. Layer interaction will need to be defined a different way if added, or throw an error if there are conflicting layer interactions per-object.
- `Intangible` moved from outer class to shape class, because there can be a mix of intangible and tangible colliders on an object.
- Removed redundant features (offset rotation, scale, matrix, axis) that can be represented through other properties.
- Removed support for multiple shapes. Multiple collision shapes can be equivalently represented with child nodes.

Collider TODOs:
- Add mesh collider support.
- Add support for other collider shapes, i.e. bullet has cylinders and cones. This isn't natively in Unity/PhysX, but could be approximated on import.