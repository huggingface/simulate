extends Node


var type : String
var content : String


func _ready() -> void:
	pass


func _process(delta : float) -> void:
	pass


func execute() -> void:
	var command_script = load("res://SimEnv/Bridge/Commands/" + type + ".gd")
	var command = command_script.new()
	command.execute(content)
