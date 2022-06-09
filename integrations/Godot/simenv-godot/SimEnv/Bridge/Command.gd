extends Node


var type : String
var content : Variant


func execute() -> void:
	var command_script = load("res://SimEnv/Commands/" + type + ".gd")
	var command = command_script.new()
	add_child(command)
	command.execute(content)
