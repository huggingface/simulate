## Simulate with Godot

### Install in Godot 4
This integration has been developed for Godot 4.x. You can install Godot from [this page](https://godotengine.org/article/dev-snapshot-godot-4-0-alpha-11).
Currently Godot4 is still in early alpha stage, therefore you will be able to find updates pretty often. Another solution is to build the engine from source using [this guide](https://docs.godotengine.org/en/latest/development/compiling/).

The integration provided is a simple Godot scene containing a default setup (with a directional light and free camera) to connect to the TCP server and load commands sent from the Simulate API.
To load it:
- Launch your Godot 4 installation
- On the Project Manager, select `Import > Browse`
- Navigate to the path of this repository and select the `integrations/Godot/simulate-godot/project.godot` file
- Finally click `Import & Edit`

You can also copy the simulate-godot folder to a different place and load it from there.

### Use the scene
- Create the `simulate` scene with a `'Godot'` engine, for example:
```
import simulate as sm

scene = sm.Scene(engine="godot")
scene += sm.Sphere()
scene.render()
```
- Run the python script. It should print "Waiting for connection...", meaning that it has spawned a websocket server, and is waiting for a connection from the Godot client.
- Press Play (F5) in Godot. It should connect to the Python client, then display a basic Sphere. The python script should finish execution.

### Add glTF extensions

The integration uses the `GLTFDocument` API to load and save glTF files. You can find the main glTF loading logic in the `simulate_godot/Simulate/Commands/initialize.gd` script.
To register new extensions, we use the `GLTFDocumentExtension` API. Currently, we register the `HFExtension` class to load every extension.

For every node found with the label `extensions`, the `_import_node` method from the registered `HFExtension` class will be called with a few arguments:
- `state`: the current `GLTFState` object which contains basically all the data and nodes.
- `gltf_node`: -- not sure what this one is for --
- `json`: json object containing all the default attributes of the node (name, id, translation, rotation, etc.)
- `node`: a temporary node in the tree that we can replace with a more adapted class. 

All extensions are mapped in the `_import_node` method. To add a new extension, you need to add a mapping following the same pattern as you can find in the file.
You can then create a new script extending a Node type that makes the most sense for the glTF extension, then import all the fields of the extensions as attributes of this node.
To see how you can access the custom attributes through `GLTFState` object, you can check how the other extension nodes are written. 

Now, when the glTF parser will find a node with the extension you defined, it'll create a node of the types you defined and fill its attributes with all the values you mapped and that are found in the glTF file.
Once all this data is imported in the scene, you can use it in any way you want. 