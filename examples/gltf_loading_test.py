from simenv import Scene

scene = Scene.load('simenv-tests/Chair', repo_filepath='glTF-Binary/SheenChair.glb')

print(scene)
print(scene._created_from_file)
scene.show(in_background=False)
print(scene)

# gltf = sm.tree_as_gltf(scene)

# print(gltf)
# gltf.export_gltf("/Users/thomwolf/Documents/GitHub/hf-simenv/playground/scene-export.gltf")

# scene2 = sm.Scene.from_gltf("/Users/thomwolf/Documents/GitHub/hf-simenv/playground/scene-export.gltf")

# scene2.show()
