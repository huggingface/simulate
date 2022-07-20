extends Node
# Close the application

signal callback


func execute(_content):
	get_tree().quit()
	get_tree().paused = false
	emit_signal("callback", PackedByteArray([97, 99, 107]))
