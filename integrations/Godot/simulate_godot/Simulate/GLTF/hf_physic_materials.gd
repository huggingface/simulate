extends GLTFDocumentExtension
class_name HFPhysicMaterial


func _import_node(state, gltf_node, json, node):
	var node_extensions = json.get("extensions")
	if not json.has("extensions"):
		return OK
	if state.base_path.is_empty():
		return OK
	if node_extensions.has("HF_physic_materials"):
		print("Physic materials found.")
		import_agents(state, json, gltf_node, node_extensions)
	return OK

func import_agents(state, json, node, extensions):
	var physic_materials = extensions["HF_physic_materials"]["objects"]
	var new_node = null
	var old_node = node

	for physic_material in physic_materials:
		for key in physic_material.keys():
			match key:
				"name":
					pass
				"dynamic_friction":
					pass
				"static_friction":
					pass
				"bounciness":
					pass
				"friction_combine":
					pass
				"bounce_combine":
					pass

	if new_node:
		node.replace_by(new_node)
		old_node.queue_free()
