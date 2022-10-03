class_name Client
extends Node
# TCP client to receive data from the python-side API
# Syncs data reception with the physics process


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

func _physics_process(_delta) -> void:
	# this is called at a fixed rate
	update_status()
	print("------------physic step--------------")

	if _status == _stream.STATUS_CONNECTED:
		get_tree().paused = true
		read()

func update_status() -> void:
	# Get the current stream status
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

func read() -> void:
	# Get data from TCP stream, only reads 1 command at a time
	while true:
		update_status()
		var available_bytes: int = _stream.get_available_bytes()
		var bytes_data: PackedByteArray = PackedByteArray()
		if available_bytes > 0:
			var msg_length: int = _stream.get_32()
			print("Message length: " + str(msg_length))
			available_bytes = _stream.get_available_bytes()
			
			# Read the data chunk by chunk until msg length is reached
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
			break
		else:
			if not _warmed_up:
				get_tree().paused = false
				break

func connect_to_host(host: String, port: int) -> void:
	# Connect to the TCP server that was setup on the python-side API
	print("Connecting to %s:%d" % [host, port])
	if _status == _stream.STATUS_CONNECTED:
		_stream.disconnect_from_host()
	
	_status = _stream.STATUS_NONE
	if _stream.connect_to_host(host, port) != OK:
		print("Error connecting to host.")
		_stream.disconnect_from_host()
		emit_signal("error")

func send(out_data: PackedByteArray) -> bool:
	# Send back data to the python-side code, usually for callbacks and obs
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
