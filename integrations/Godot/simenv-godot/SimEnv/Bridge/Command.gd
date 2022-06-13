extends Node
class_name Command

var type : String
var content : Variant
var command
var commands : Dictionary

func load_commands():
	var directory: Directory = Directory.new()
	var com_path : String = "res://SimEnv/Commands"
	directory.open(com_path)
	directory.list_dir_begin()

	while true:
		var file = directory.get_next()
		if file == "":
			break

		var command_name = file.split(".")[0]
		var command_script = load(com_path + "/" + file)
		commands[command_name] = command_script.new()
		add_child(commands[command_name])

	directory.list_dir_end()

func execute(type: String) -> void:
	if type in commands:
		commands[type].execute(content)
	else:
		print("Unknown command.")
