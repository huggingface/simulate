extends GLTFDocumentExtension
class_name HFStateSensor


func _import_node(state, gltf_node, json, node):
	var node_extensions = json.has("extensions")
	if not json.has("extensions"):
		return OK
	if state.base_path.is_empty():
		return OK
	if node_extensions.get("HF_state_sensors"):
		print("State sensors found.")
		import_agents(state, json, gltf_node, node_extensions)
	return OK

func import_agents(state, json, node, extensions):
	var state_sensors = extensions["HF_state_sensors"]["objects"]
	var new_node = null
	var old_node = node

	for state_sensor in state_sensors:
		for key in state_sensor.keys():
			match key:
				"target_entity":
					pass
				"reference_entity":
					pass
				"properties":
					pass
				"sensor_name":
					pass

	if new_node:
		node.replace_by(new_node)
		old_node.queue_free()
