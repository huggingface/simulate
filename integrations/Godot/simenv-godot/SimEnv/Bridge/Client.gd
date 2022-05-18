extends Node3D

var client
var wrapped_client
var connected = false
var message_center
var should_connect = false


func _ready():
	client = StreamPeerTCP.new()
	client.set_no_delay(true)
	

func _process(delta):
	if should_connect and not connected:
		pass
	if connected and not client.get_status() == StreamPeerTCP.STATUS_CONNECTED:
		connected = false
	if client.get_status() == StreamPeerTCP.STATUS_CONNECTED:
		poll_server()


func connect_to_server(timeout_seconds):
	set_process(true)
	should_connect = true
	var ip = "127.0.0.1"
	var port = 55000
	print("Connecting to server: %s : %s" % [ip, str(port)])
	var connect = client.connect_to_host(ip, port)
	
	if client.is_connected_to_host():
		connected = true
		print("Connected to local host server")
	
		wrapped_client = PacketPeerStream.new()
		wrapped_client.set_stream_peer(client)


func disconnect_from_server():
	client.disconnect_from_host()


func poll_server():	
	while wrapped_client.get_available_packet_count() > 0:
		var msg = wrapped_client.get_var()
		var error = wrapped_client.get_packet_error()
		
		if error != 0:
			print("Error on packet get: %s" % error)
		if msg == null:
			continue;
		
		print("Received msg: " + str(msg))
		message_center.process_msg(str(msg))


func send_var(msg):
	if client.is_connected_to_host():
		print("Sending: %s" % msg)
		wrapped_client.put_var(msg)
		var error = wrapped_client.get_packet_error()
		
		if error != 0:
			print("Error on packet put: %s" % error)
