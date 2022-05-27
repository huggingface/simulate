extends Node


func _ready():
	pass # Replace with function body.


func _process(_delta : float):
	pass


func execute(content):
	# var decoded_content : String = Marshalls.base64_to_utf8(content["b64bytes"])
	var content_bytes : PackedByteArray = Marshalls.base64_to_raw(content["b64bytes"])
	
	var gltf_state : GLTFState = GLTFState.new()
	var gltf_doc : GLTFDocument = GLTFDocument.new()
	
	gltf_doc.append_from_buffer(content_bytes, "", gltf_state)
	var gltf_scene = gltf_doc.generate_scene(gltf_state)
	
	add_child(gltf_scene)
	print("glTF scene built!")
	
	for _i in self.get_children():
		print(_i)
