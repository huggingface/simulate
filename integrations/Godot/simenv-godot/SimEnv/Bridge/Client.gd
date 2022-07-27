class_name Client
extends Node
# This class sets up the TCP client to receive data
# from the Python SimEnv API through the TCP server
#
# Reading the stream is synchronized on the _physics_process
# Physics will only step if the command received tells it to do so
# (see SimEnv/Commands/step.gd)
#
# Data is received by chunks of _chunk_size
# _warmed_up is a hacky bugfix to start the TCP stream before the physics sync


signal connected
signal data
signal disconnected
signal error

var _status: int = 0
var _stream: StreamPeerTCP = StreamPeerTCP.new()
var _chunk_size: int = 1024
var _warmed_up: bool = false


func _ready() -> void:
	_status = _stream.get_status()


func _physics_process(_delta):
	# this is called at a fixed rate
	update_status()

	if _status == _stream.STATUS_CONNECTED:
		# to sync commands with the physics steps
		get_tree().paused = true
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
	update_status()
	var available_bytes: int = _stream.get_available_bytes()
	var bytes_data: PackedByteArray = PackedByteArray()
	if available_bytes > 0:
		var msg_length: int = _stream.get_32()
		print("Message length: " + str(msg_length))
		available_bytes = _stream.get_available_bytes()
		while len(bytes_data) < msg_length:
			var stream_data: Array = _stream.get_partial_data(min(_chunk_size, msg_length - len(bytes_data)))
			if stream_data[0] != OK:
				print("Error getting data from stream: ", stream_data[0])
				emit_signal("error")
				break
			else:
				bytes_data += stream_data[1]
				available_bytes = _stream.get_available_bytes()
	if len(bytes_data) > 0:
		emit_signal("data", bytes_data)
		_warmed_up = true
	else:
		if _warmed_up:
			read()
		else:
			get_tree().paused = false


func connect_to_host(host: String, port: int) -> void:
	print("Connecting to %s:%d" % [host, port])
	if _status == _stream.STATUS_CONNECTED:
		_stream.disconnect_from_host()
	_status = _stream.STATUS_NONE
	if _stream.connect_to_host(host, port) != OK:
		print("Error connecting to host.")
		_stream.disconnect_from_host()
		emit_signal("error")


func send(out_data: PackedByteArray) -> bool:
	if _status != _stream.STATUS_CONNECTED:
		print("Error: Stream is not currently connected.")
		return false
	var stream_error: int = _stream.put_data(PackedByteArray([len(out_data)]))
	if stream_error != OK:
		print("Error writing to stream: ", error)
		return false
	stream_error = _stream.put_data(out_data)
	if stream_error != OK:
		print("Error writing to stream: ", error)
		return false
	return true
