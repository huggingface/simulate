class_name RLManager
extends Node


var root
var actors


func load_nodes():
	root = Simulator.get_node("Scene/scene_00")
	for child in Simulator.get_all_children(root):
		if "is_actor" in child and child.is_actor:
			actors.append(Actor.new(child))
