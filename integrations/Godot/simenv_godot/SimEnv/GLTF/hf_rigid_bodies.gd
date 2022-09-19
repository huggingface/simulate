extends GLTFDocumentExtension
class_name HFRigidBody


func _import_node(state, gltf_node, json, node):
	var node_extensions = json.get("extensions")
	if not json.has("extensions"):
		return OK
	if state.base_path.is_empty():
		return OK
	if node_extensions.has("HF_rigid_bodies"):
		print("Rigid bodies found.")
		import_agents(state, json, gltf_node, node_extensions)
	return OK

func import_agents(state, json, node, extensions):
	var rigid_bodies = extensions["HF_rigid_bodies"]["objects"]
	var new_node = null
	var old_node = node
	
	for rigid_body in rigid_bodies:
		for key in rigid_body.keys():
			match key:
				"name":
					pass
				"mass":
					pass
				"center_of_mass":
					pass
				"inertia_tensor":
					pass
				"linear_drag":
					pass
				"angular_drag":
					pass
				"constraints":
					pass
				"use_gravity":
					pass
				"collision_detection":
					pass
				"kinematic":
					pass
	
	if new_node:
		node.replace_by(new_node)
		old_node.queue_free()
