extends GLTFDocumentExtension
class_name HFArticulationBody


func _import_node(state, gltf_node, json, node):
	var node_extensions = json.get("extensions")
	if not json.has("extensions"):
		return OK
	if state.base_path.is_empty():
		return OK
	if node_extensions.has("HF_articulation_bodies"):
		print("Articulation bodies found.")
		import_agents(state, json, gltf_node, node_extensions)
	return OK

func import_agents(state, json, node, extensions):
	var articulation_bodies = extensions["HF_articulation_bodies"]["objects"]
	var new_node = null
	var old_node = node

	for articulation_body in articulation_bodies:
		for key in articulation_body.keys():
			match key:
				"joint_type":
					pass
				"anchor_rotation":
					pass
				"anchor_position":
					pass
				"inertia_tensor":
					pass
				"immovable":
					pass
				"linear_damping":
					pass
				"angular_damping":
					pass
				"joint_friction":
					pass
				"drive_stifness":
					pass
				"drive_damping":
					pass
				"drive_force_limit":
					pass
				"drive_target":
					pass
				"drive_target_velocity":
					pass
				"is_limited":
					pass
				"upper_limit":
					pass
				"lower_limit":
					pass

	if new_node:
		node.replace_by(new_node)
		old_node.queue_free()
