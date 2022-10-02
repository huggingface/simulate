extends Node
# Reset the simulation


signal callback


func execute(_content:Variant) -> void:
	get_tree().paused = false
	emit_signal("callback", PackedByteArray([97, 99, 107]))
