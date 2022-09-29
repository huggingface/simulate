extends Node
# Core of the integration and base of the scene
# Handles data received from the client and call commands


const HOST : String = "127.0.0.1"
const PORT : int = 55001
const RECONNECT_TIMEOUT: float = 3.0

var _client : Client = Client.new()
var _command : Command = Command.new()

var agent


func _ready() -> void:
	# Connect to signals, load client and commands
	_client.connect("connected", _handle_client_connected)
	_client.connect("disconnected", _handle_client_disconnected)
	_client.connect("error", _handle_client_error)
	_client.connect("data", _handle_client_data)
	_command.connect("callback", _handle_callback)

	add_child(_client)
	add_child(_command)
	
	_command.load_commands()
	_client.connect_to_host(HOST, PORT)

func _connect_after_timeout(timeout: float) -> void:
	# Retry connection after given timeout
	await get_tree().create_timer(timeout).timeout
	_client.connect_to_host(HOST, PORT)

func _handle_client_connected() -> void:
	print("Client connected to server.")

func _handle_client_data(data: PackedByteArray) -> void:
	# Parse data and sends content for command execution
	var str_data : String = data.get_string_from_utf8()
	
	var json_object : JSON = JSON.new()
	if json_object.parse(str_data) == OK:
		var json_data : Variant = json_object.get_data()
		var command_type: String = json_data["type"]
		json_data.erase("type")
		_command.content = json_data
		_command.execute(command_type)
		print("Command: " + command_type)
		if get_tree().paused:
			_client.read()
	else:
		print("Error parsing data.")

func _handle_client_disconnected() -> void:
	# Reconnect client if it gets disconnected
	print("Client disconnected from server.")
	_connect_after_timeout(RECONNECT_TIMEOUT)

func _handle_client_error() -> void:
	# Reconnect client if there is an error
	print("Client error.")
	_connect_after_timeout(RECONNECT_TIMEOUT)

func _handle_callback(callback_data: PackedByteArray) -> void:
	# Send callback to python-side API
	print("Sending callback.")
	_client.send(callback_data)
