extends Node

const HOST : String = "127.0.0.1"
const PORT : int = 55000
const RECONNECT_TIMEOUT: float = 3.0

var _client : Client = Client.new()
var _command : Command = Command.new()

func _ready() -> void:
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
	await get_tree().create_timer(timeout).timeout
	_client.connect_to_host(HOST, PORT)

func _handle_client_connected() -> void:
	print("Client connected to server.")

func _handle_client_data(data: PackedByteArray) -> void:
	# The first 4 bytes are the message length TODO: remove slice when chunking is implemented
	var str_data : String = data.slice(4).get_string_from_utf8()
	print("Start: ", str_data.left(60), "...", str_data.right(30))
	
	var json_object : JSON = JSON.new()
	if json_object.parse(str_data) == OK:
		var json_data : Variant = json_object.get_data()
		_command.content = json_data["contents"]
		_command.execute(json_data["type"])
	else:
		print("Error parsing data.")

func _handle_client_disconnected() -> void:
	print("Client disconnected from server.")
	_connect_after_timeout(RECONNECT_TIMEOUT)

func _handle_client_error() -> void:
	print("Client error.")
	_connect_after_timeout(RECONNECT_TIMEOUT)
	
func _handle_callback(callback_data: PackedByteArray) -> void:
	print("Sending callback.")
	_client.send(callback_data)
