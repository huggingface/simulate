extends GLTFDocumentExtension
class_name HFExtensions


func _import_node(state: GLTFState, _gltf_node: GLTFNode, json: Dictionary, node: Node):
	var extensions = json.get("extensions")
	if not json.has("extensions"):
		return OK
	
	if extensions.has("HF_actuators"):
		var actuator = HFActuator.new()
		actuator.import(state, json, extensions)
		node.replace_by(actuator)
	if extensions.has("HF_articulation_bodies"):
		var articulation_body = HFArticulationBody.new()
		articulation_body.import(state, json, extensions)
		node.replace_by(articulation_body)
	if extensions.has("HF_colliders"):
		var collider = HFCollider.new()
		collider.import(state, json, extensions)
		node.replace_by(collider)
	if extensions.has("HF_raycast_sensors"):
		var raycast_sensor = HFRaycastSensor.new()
		raycast_sensor.import(state, json, extensions)
		node.replace_by(raycast_sensor)
	if extensions.has("HF_reward_functions"):
		var reward_function = HFRewardFunction.new()
		reward_function.import(state, json, extensions)
		node.replace_by(reward_function)
	if extensions.has("HF_rigid_bodies"):
		var rigid_body = HFRigidBody.new()
		rigid_body.import(state, json, extensions)
		node.replace_by(rigid_body)
	if extensions.has("HF_state_sensors"):
		var state_sensor = HFStateSensor.new()
		state_sensor.import(state, json, extensions)
		node.replace_by(state_sensor)
	
	return OK
