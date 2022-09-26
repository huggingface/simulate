This package provides core backend functionality for the Hugging Face Simulate project: (https://github.com/huggingface/simulate).

To use this package, add a GameObject to the scene, then add a `Simulator` component to it.

Core Classes:
- `Simulator`: Master controller singleton that tracks objects, loads and unloads plugins, etc.
- `Node`: Component attached to every tracked object.
- `RenderCamera`: Component attached to every tracked camera. Call `Render()` to asynchronously request a color buffer.
- `Client`: Manages communication with the backend. Don't modify directly; instead, use plugins.

Plugins:
- `IPlugin`: For adding custom behaviour to the backend.
- `ICommand`: For defining custom commands from the Python frontend.
- `IGLTFExtension`: For defining custom GLTF extensions.

To add functionality to the backend:
- Create a separate folder. For example, `RLAgents`.
- Add an assembly definition to this folder (Right Click > Create > Assembly Definition).
- In the assembly definition, add a reference to `Simulate`.
- In the folder, create a script that implements `IPlugin`. For a simple example, look at `IPlugin.cs`, or for a more complex example, see `AgentsPlugin.cs`.

If this folder is in the Unity project, it will automatically be included in the build.

To add functionality post-build, a plugin can be compiled externally, then the DLL can be placed in the build's `Resources/Plugins/` folder.
