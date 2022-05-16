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

Project Structure
---
The Python API is located in src/simenv. It allows creation and loading of scenes, and sending commands to the backend.

The backend, currently just Unity, is located in integrations/Unity. This is currently a Unity editor project, which must be opened in Unity 2021.3.2f1. In the future, this will be built as an executable, and spawned by the Python API.

Creating a Scene
---
Basic example of creating a scene with a sphere:
```
import simenv as sm

scene = sm.Scene()
scene += sm.Sphere()
```

Rendering in Unity Example
---
1. Open the Unity project, then open the Sample Scene, or create a new scene and add an empty GameObject with a `Client.cs` component attached.
2. Add the Unity backend to your scene, and render it. For example, modifying the above example:
```
import simenv as sm

scene = sm.Scene(engine="Unity")
scene += sm.Sphere()
scene.render()
```
3. Run the python script. It should print "Waiting for connection...", meaning that it has spawned a websocket server, and is waiting for a connection from the Unity client.
4. Press Play in Unity. It should connect to the Python client, then display a basic Sphere. The python script should finish execution.

Creating Custom Functionality
---
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
