extends Node
# Close the simulation


signal callback


func execute(_content: Variant) -> void:
	get_tree().paused = false
	get_tree().quit()
	print("Close called!")
	emit_signal("callback", PackedByteArray([97, 99, 107]))
