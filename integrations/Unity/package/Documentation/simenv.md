This plugin provides support for creating and sharing environments in Unity, for the Hugging Face Simulation Environment project (https://github.com/huggingface/simenv).

Installation

From Git

---

1. Open package manager in Unity (Window -> Package Manager)
2. Click "+" -> "Add package from git URL"
3. Install from the URL: "https://github.com/dylanebert/simenv.git?path=/integrations/Unity/package"

From File

---

1. Place the SimEnv `integrations/Unity/package` folder in a known location
2. Open package manager in Unity (Window -> Package Manager)
3. Click "+" -> "Add package from disk"
4. Locate the `package.json` file in the `integrations/Unity/package` folder

Setup

1. In a new scene, add an empty GameObject (GameObject -> Create Empty)
2. Add a Client component to the GameObject (Add Component -> Client)