extends GLTFDocumentExtension
class_name HFActuators


var objects: Array


func _import_node(state, gltf_node, json, node):
	var node_extensions = json.get("extensions")
	print("Import extension nodes!")
	if not json.has("extensions"):
		return OK
	if state.base_path.is_empty():
		return OK
	if node_extensions.has("HF_actuators"):
		print("Actuators found.")
		import_agents(state, json, gltf_node, node_extensions)
	return OK

func import_agents(state, json, node, extensions):
	var actuators = extensions["HF_actuators"]["objects"]
	var new_node = null
	var old_node = node

	for actuactor in actuators:
		var hf_actuator: HFActuator = HFActuator.new()
		for key in actuactor.keys():
			match key:
				"mapping":
					pass
				"n":
					pass
				"dtype":
					pass
				"low":
					pass
				"high":
					pass
				"shape":
					pass
				_:
					print("Field not implemented")

	if new_node:
		node.replace_by(new_node)
		old_node.queue_free()


class HFActuator:
	var mapping: ActionMapping
	var n: int
	var dtype: String
	var low: Array
	var high: Array
	var shape: Array


class ActionMapping:
	var action: String
	var amplitude: float
	var offset: float
	var axis: Vector3
	var position: Vector3
	var use_local_coordinates: bool
	var is_impulse: bool
	var max_velocity_threshold: float


class ActionSpace:
	var action_map: Array

	func _init(mapping: Array):
		self.action_map = mapping

	func get_mapping(key) -> ActionMapping:
		var index: int = int(key)
		return self.action_map[index]
