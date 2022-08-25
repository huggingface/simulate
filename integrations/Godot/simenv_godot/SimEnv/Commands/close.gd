extends Node
# Close the simulation


signal callback


func execute(_content):
	get_tree().paused = false
	get_tree().notification(MainLoop.NOTIFICATION_WM_QUIT_REQUEST)
	print("Close called!")
	emit_signal("callback", PackedByteArray([97, 99, 107]))
