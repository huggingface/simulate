## Blender Integration

### Install addon in Blender
This integration has been developed for Blender 3.2. You can install Blender from [this page](https://www.blender.org/download/)

- Launch Blender
- Go to `Edit > Preferences > Add-ons > Install...`  
- Select the `simulate_blender.zip` file next to this README.md file

### Run in Blender
- You might need to run Blender with admin rights
- You can find an example script using the `simulate` API in `simulate/examples/blender_example.py` to create a scene
- Run the python script. It should print "Waiting for connection...", meaning that it has spawned a websocket server, and is waiting for a connection from the Blender client
- In Blender, open the submenus (little arrow in the top right)
- Go in the `Simulation` category and click on `Import Scene`. It should connect to the Python client, then display the scene. The python script should finish execution
- If you call `scene.render(path)`, Blender might freeze for a bit while rendering the scene to an image

