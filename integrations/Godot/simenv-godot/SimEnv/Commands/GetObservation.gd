extends Node

signal callback

func execute(_content):
	emit_signal("callback", PackedByteArray([97, 99, 107]))
