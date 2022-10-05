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

