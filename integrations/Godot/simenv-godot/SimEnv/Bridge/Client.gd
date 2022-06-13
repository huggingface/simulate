extends Node
class_name Client

signal connected
signal data
signal disconnected
signal error

var _status: int = 0
var _stream: StreamPeerTCP = StreamPeerTCP.new()

func _ready() -> void:
	_status = _stream.get_status()

func _process(_delta: float) -> void:
	update_status()
	read()

func update_status():
	_stream.poll()
	var new_status: int = _stream.get_status()
	if new_status != _status:
		_status = new_status
		match _status:
			_stream.STATUS_NONE:
				print("Disconnected from host.")
				emit_signal("disconnected")
			_stream.STATUS_CONNECTING:
				print("Connecting to host.")
			_stream.STATUS_CONNECTED:
				print("Connected to host.")
				emit_signal("connected")
			_stream.STATUS_ERROR:
				print("Error with socket stream.")
				emit_signal("error")

func read():
	if _status == _stream.STATUS_CONNECTED:
		var available_bytes: int = _stream.get_available_bytes()
		if available_bytes > 0:
			print("Available bytes: ", available_bytes)
			var stream_data: Array = _stream.get_partial_data(available_bytes)
			if stream_data[0] != OK:
				print("Error getting data from stream: ", stream_data[0])
				emit_signal("error")
			else:
				emit_signal("data", stream_data[1])

func connect_to_host(host: String, port: int) -> void:
	print("Connecting to %s:%d" % [host, port])
	
	if _status == _stream.STATUS_CONNECTED:
		_stream.disconnect_from_host()
	
	_status = _stream.STATUS_NONE
	if _stream.connect_to_host(host, port) != OK:
		print("Error connecting to host.")
		emit_signal("error")

func send(out_data: PackedByteArray) -> bool:
	if _status != _stream.STATUS_CONNECTED:
		print("Error: Stream is not currently connected.")
		return false
	var stream_error: int = _stream.put_data(out_data)
	if stream_error != OK:
		print("Error writing to stream: ", error)
		return false
	return true
