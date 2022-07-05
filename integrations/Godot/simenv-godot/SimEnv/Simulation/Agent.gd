extends Node
class_name Agent


class Actions:
	var name: 		String
	var dist: 		String
	var available: 	Array = []
	var forward: 	float = 0.0
	var move_right: float = 0.0
	var turn_right: float = 0.0
	
	func set_action(step_action: Array) -> void:
		pass


class DiscreteActions:
	extends Actions
	
	func set_action(step_action: Array) -> void:
		var istep_action: int = int(step_action[0])
		forward = 0.0
		move_right = 0.0
		turn_right = 0.0
		
		match available[istep_action]:
			"move_foward":
				forward = 1.0
			"move_backward":
				forward = -1.0
			"move_left":
				move_right = 1.0
			"move_right":
				move_right = -1.0
			"turn_right":
				turn_right = 1.0
			"turn_left":
				turn_right = -1.0
			_:
				print("Invalid action.")


class ContinuousActions:
	extends Actions
	
	func set_action(step_action: Array) -> void:
		for i in range(len(step_action)):
			match available[i]:
				"move_forward_backward":
					forward = step_action[i]
				"move_left_right":
					move_right = step_action[i]
				"turn_left_right":
					turn_right = step_action[i]
				_:
					print("Invalid action.")


# Called when the node enters the scene tree for the first time.
func _ready():
	pass # Replace with function body.


# Called every frame. 'delta' is the elapsed time since the previous frame.
func _process(delta):
	pass
