extends Node



# Called when the node enters the scene tree for the first time.
func _ready():
	pass # Replace with function body.


# Called every frame. 'delta' is the elapsed time since the previous frame.
func _process(_delta : float):
	pass


func execute(content):
	var decoded_content : String = Marshalls.base64_to_utf8(content["b64bytes"])
	print("Command executed: ", decoded_content)
