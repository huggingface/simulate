class_name HFExtensions
extends GLTFDocumentExtension


func _import_node(state: GLTFState, _gltf_node: GLTFNode, json: Dictionary, node: Node):
	var extensions = json.get("extensions")
	if not json.has("extensions"):
		return OK
	
	var new_node
	if extensions.has("HF_rigid_bodies"):
		new_node = HFRigidBody.new()
	if extensions.has("HF_articulation_bodies"):
		new_node = HFArticulationBody.new()
	if extensions.has("HF_colliders"):
		new_node = HFCollider.new()
	if extensions.has("HF_raycast_sensors"):
		new_node = HFRaycastSensor.new()
	if extensions.has("HF_reward_functions"):
		new_node = HFRewardFunction.new()
	if extensions.has("HF_state_sensors"):
		new_node = HFStateSensor.new()
	
	if new_node:
		new_node.import(state, json, extensions)
		if extensions.has("HF_actuators") and "actuator" in new_node:
			new_node.actuator = HFActuator.new()
			new_node.actuator.import(state, json, extensions)
		node.replace_by(new_node)
	else:
		print("Extension not implemented.")
	return OK
