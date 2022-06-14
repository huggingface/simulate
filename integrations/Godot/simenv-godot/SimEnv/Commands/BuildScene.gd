extends Node


func execute(content):
	var content_bytes : PackedByteArray = Marshalls.base64_to_raw(content["b64bytes"])
	
	var gltf_state : GLTFState = GLTFState.new()
	var gltf_doc : GLTFDocument = GLTFDocument.new()
	
	gltf_doc.append_from_buffer(content_bytes, "", gltf_state)
	var gltf_scene = gltf_doc.generate_scene(gltf_state)
	
	get_tree().current_scene.add_child(gltf_scene)
	print("glTF scene built!")
