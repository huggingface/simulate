class_name Command
extends Node


var content : Variant
var _commands : Dictionary


func load_commands() -> void:
	var com_path : String = "res://Simulate/Commands"
	var directory = DirAccess.open(com_path)
	
	if directory:
		directory.list_dir_begin()
		while true:
			var file = directory.get_next()
			if file == "":
				break
			var command_name = file.split(".")[0]
			var command_script = load(com_path + "/" + file)
			_commands[command_name] = command_script.new()
		directory.list_dir_end()


func execute(type: String) -> void:
	if type in _commands:
		_commands[type].execute(content)
	else:
		print("Unknown command.")
		Simulator.send_callback("{}")
