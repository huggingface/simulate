extends Node
# Close the simulation


func execute(_content: Variant) -> void:
	Simulator.get_tree().paused = false
#	Simulator.get_tree().quit()
	Simulator.send_callback("{}")
