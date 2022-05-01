// based on https://github.com/Moguri/glTF/tree/panda3d_physics_collision_shapes/extensions/2.0/Vendor/PANDA3D_collision_shapes
using UnityEngine;
using Newtonsoft.Json;

public class GLTFCollider
{
    [JsonConverter(typeof(EnumConverter))] public ColliderType type = ColliderType.BOX;
    [JsonProperty(Required = Required.Always)] public float[] boundingBox;
    public string primaryAxis = "Y";
    public int mesh;
    [JsonConverter(typeof(Matrix4x4Converter))] public Matrix4x4 offsetMatrix = Matrix4x4.identity;
    [JsonConverter(typeof(Vector3Converter))] public Vector3 offsetTranslation = Vector3.zero;
    [JsonConverter(typeof(QuaternionConverter))] public Quaternion offsetRotation = Quaternion.identity;
    [JsonConverter(typeof(Vector3Converter))] public Vector3 offsetScale = Vector3.one;
}
