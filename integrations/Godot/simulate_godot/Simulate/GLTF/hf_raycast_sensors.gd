extends GLTFDocumentExtension
class_name HFRaycastSensor


func _import_node(state, gltf_node, json, node):
	var node_extensions = json.get("extensions")
	if not json.has("extensions"):
		return OK
	if state.base_path.is_empty():
		return OK
	if node_extensions.has("HF_raycast_sensors"):
		print("Raycast sensors found.")
		import_agents(state, json, gltf_node, node_extensions)
	return OK

func import_agents(state, json, node, extensions):
	var raycast_sensors = extensions["HF_raycast_sensors"]["objects"]
	var new_node = null
	var old_node = node

	for raycast_sensor in raycast_sensors:
		for key in raycast_sensor.keys():
			match key:
				"n_horizontal_rays":
					pass
				"n_vertical_rays":
					pass
				"horizontal_fov":
					pass
				"vertical_fov":
					pass
				"ray_length":
					pass
				"sensor_name":
					pass

	if new_node:
		node.replace_by(new_node)
		old_node.queue_free()
