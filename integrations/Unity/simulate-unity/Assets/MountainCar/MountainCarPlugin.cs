using System.Collections.Generic;
using Simulate;
using UnityEngine;

public class MountainCarPlugin : PluginBase {
    public override void OnSceneInitialized(Dictionary<string, object> kwargs) {
        GameObject cart = GameObject.Find("Cart");
        GameObject rail = GameObject.Find("RailCollider");
        if (cart != null && rail != null) {
            Debug.Log("Found cart and rail objects, setting up mountain car plugin");
            cart.AddComponent<Cart>();
            rail.layer = LayerMask.NameToLayer("Ground");
        }
    }
}