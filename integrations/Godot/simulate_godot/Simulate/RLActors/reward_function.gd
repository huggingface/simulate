class_name RewardFunction
extends Node


var entity_a: Node3D
var entity_b: Node3D
var reward_scalar: float = 1.0
var distance_metric: DistanceMetric


func reset() -> void:
	pass


func calculate_reward() -> float:
	return 0.0


class DistanceMetric:
	func Calculate(e1: Node3D, e2: Node3D) -> float:
		return 0.0


class EuclideanDistance:
	extends DistanceMetric
	
	func Calculate(e1: Node3D, e2: Node3D) -> float:
		return e1.position.distance_to(e2.position)


class CosineDistance:
	extends DistanceMetric
	
	func Calculate(e1: Node3D, e2: Node3D) -> float:
		return e1.position.distance_to(e2.position)


class DenseRewardFunction:
	extends RewardFunction
	
	var best_distance: float = INF
	
	func _init(entity_a, entity_b, distance_metric, reward_scalar):
		pass
	
	func reset() -> void:
		pass
	
	func calculate_reward() -> float:
		return 0.0


class SparseRewardFunction:
	extends RewardFunction
	
	var has_triggered: bool = false
	var is_terminal: bool = false
	var is_collectable: bool = false
	var trigger_once: bool = true
	var threshold: float = 1.0
	
	func _init(entity_a, entity_b, distance_metric, reward_scalar, threshold, is_terminal, is_collectable, trigger_once):
		pass
	
	func reset() -> void:
		pass
	
	func calculate_reward() -> float:
		return 0.0


class SeeRewardFunction:
	extends SparseRewardFunction
	
	func _init(entity_a, entity_b, distance_metric, reward_scalar, threshold, is_terminal, is_collectable, trigger_once):
		pass
	
	func reset() -> void:
		pass
	
	func calculate_reward() -> float:
		return 0.0


class RewardFunctionPredicate:
	extends RewardFunction
	
	var reward_function_a: RewardFunction
	var reward_function_b: RewardFunction = null
	var has_triggered: bool = false
	var is_terminal: bool = false
	
	func _init(reward_function_a, reward_function_b, entity_a, entity_b, distance_metric, is_terminal):
		pass
	
	func reset() -> void:
		pass


class RewardFunctionAnd:
	extends RewardFunctionPredicate
	
	func _init(reward_function_a, reward_function_b, entity_a, entity_b, distance_metric, is_terminal):
		pass
	
	func calculate_reward() -> float:
		return 0.0


class RewardFunctionOr:
	extends RewardFunctionPredicate
	
	func _init(reward_function_a, reward_function_b, entity_a, entity_b, distance_metric, is_terminal):
		pass
	
	func calculate_reward() -> float:
		return 0.0


class RewardFunctionXor:
	extends RewardFunctionPredicate
	
	func _init(reward_function_a, reward_function_b, entity_a, entity_b, distance_metric, is_terminal):
		pass
	
	func calculate_reward() -> float:
		return 0.0


class RewardFunctionNot:
	extends RewardFunctionPredicate
	
	func _init(reward_function_a, reward_function_b, entity_a, entity_b, distance_metric, is_terminal):
		pass
	
	func calculate_reward() -> float:
		return 0.0


class TimeoutRewardFunction:
	extends SparseRewardFunction
	var steps: int = 0
	
	func _init(entity_a, entity_b, distance_metric, reward_scalar, threshold, is_terminal, is_collectable, trigger_once):
		pass
	
	func reset() -> void:
		pass
	
	func calculate_reward() -> float:
		return 0.0
