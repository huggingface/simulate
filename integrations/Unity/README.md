## Unity Integration

### Install with the Unity editor
Currently we use Unity version `2021.3.2f1` as the development version.

To install and run the project in Unity:
- First install Unity `2021.3.2f1` using the Unity Hub if you don't have it. 
- From the Unity Hub, open the project at `./integrations/Unity/simulate-unity`
- Open the Sample Scene or create a new scene with an empty GameObject with a `Client.cs` component attached

(Note that installation of this specific version on Apple Silicon Mac's has been tricky -- to do so, first install Unity Hub, then download the [source](https://unity3d.com/get-unity/download/archive) package from Unity directly, then install the package. 
It is easiest to do this from a fresh Unity install; detecting the second from-source Unity editor version is more challenging.)

### Run with the Unity engine
1. If it's not already opened, open the Unity project with Scene with a GameObject with a `Client.cs` component attached.
2. Create the `simulate` scene with a `'Unity'` engine, for example:
```
import simulate as sm

scene = sm.Scene(engine="unity")
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
using Simulate;

public class MyCommand : Command {
    public string message;
    
    public override void Execute(UnityAction<string> callback) {
        Debug.Log(message);
        callback("{}");
    }
}
```

Simply adding the script to the project should be sufficient to make it work. Any public fields defined in a `Command` can be passed through your `contents` JSON. Only simple types (i.e. `int`, `float`, `string`) and arrays are supported, not Lists, Vector3, etc., since it uses Unity's built-in JSON serialization. You need to serialize/deserialize these yourself.

### Colliders Extension
The HF_colliders extension is based loosely on the PANDA3D_physics_collision_shapes extension: https://github.com/Moguri/glTF/tree/panda3d_physics_collision_shapes/extensions/2.0/Vendor/PANDA3D_collision_shapes

This extension is defined both at the scene-level (storing the colliders) and the node-level (storing pointers to the colliders). For example, a node with a box collider:
```
{
    "extensions": {
        "HF_colliders": {
            collider: {
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
