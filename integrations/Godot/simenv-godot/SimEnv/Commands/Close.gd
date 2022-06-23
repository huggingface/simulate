extends Node

signal callback

func execute(_content):
	get_tree().quit()
	emit_signal("callback", PackedByteArray([97, 99, 107]))
