extends GLTFDocumentExtension
class_name HFRewardFunction


func _import_node(state, gltf_node, json, node):
	var node_extensions = json.get("extensions")
	if not json.has("extensions"):
		return OK
	if state.base_path.is_empty():
		return OK
	if node_extensions.has("HF_reward_functions"):
		print("Reward functions found.")
		import_agents(state, json, gltf_node, node_extensions)
	return OK

func import_agents(state, json, node, extensions):
	var reward_functions = extensions["HF_reward_functions"]["objects"]
	var new_node = null
	var old_node = node

	for reward_function in reward_functions:
		for key in reward_function.keys():
			match key:
				"type":
					pass
				"entity_a":
					pass
				"entity_b":
					pass
				"distance_metric":
					pass
				"direction":
					pass
				"scalar":
					pass
				"threshold":
					pass
				"is_terminal":
					pass
				"is_collectable":
					pass
				"trigger_once":
					pass

	if new_node:
		node.replace_by(new_node)
		old_node.queue_free()
