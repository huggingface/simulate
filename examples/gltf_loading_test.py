import simenv as sm

scene = sm.Scene.load_from_hub(repo_id='simenv-tests/BoxTextured', subfolder='glTF', filename="BoxTextured.gltf")

print(scene)
scene.show(in_background=False)
print(scene)

# gltf = sm.tree_as_gltf(scene)

# print(gltf)
# gltf.export_gltf("/Users/thomwolf/Documents/GitHub/hf-simenv/playground/scene-export.gltf")

# scene2 = sm.Scene.from_gltf("/Users/thomwolf/Documents/GitHub/hf-simenv/playground/scene-export.gltf")

# scene2.show()
