using System.Collections.Generic;
using UnityEngine;

namespace SimEnv {
    public class RaycastSensor : ISensor {
        public string mName = "RaycastSensor";
        public static string mType = "float";
        public Node node => m_node;
        Node m_node;

        private List<(float horizontal, float vertical)> raycastAngles;
        private int nHorizontalRays = -1;
        private int nVerticalRays = -1;

        private float horizontalFOV = 0;
        private float verticalFOV = 0;
        private float rayLength = 0;


        public RaycastSensor(Node node, SimEnv.GLTF.HFRaycastSensors.HFRaycastSensor data) {
            m_node = node;
            node.sensor = this;
            mName = data.sensor_name;
            // calculate ray angles etc
            Debug.Log("instantiating raycast sensor");

            nHorizontalRays = data.n_horizontal_rays;
            nVerticalRays = data.n_vertical_rays;
            horizontalFOV = data.horizontal_fov;
            verticalFOV = data.vertical_fov;
            rayLength = data.ray_length;

            ComputeRaycastAngles();
        }

        private void ComputeRaycastAngles() {
            raycastAngles = new List<(float horizontal, float vertical)>();
            float horizontalStep = horizontalFOV / nHorizontalRays;
            float verticalStep = verticalFOV / nVerticalRays;

            var horizontalStart = (horizontalStep - horizontalFOV) / 2;
            var verticalStart = (verticalStep - verticalFOV) / 2;

            for (int i = 0; i < nHorizontalRays; i++) {
                for (int j = 0; j < nVerticalRays; j++) {
                    var angleH = horizontalStart + i * horizontalStep;
                    var angleV = verticalStart + j * verticalStep;
                    raycastAngles.Add((angleH, angleV));
                }
            }
        }

        public string GetName() {
            return mName;
        }

        public string GetSensorType() {
            return mType;
        }

        public int GetSize() {
            return raycastAngles.Count;
        }

        public int[] GetShape() {
            int[] shape = { GetSize() };
            return shape;
        }

        public string GetBufferType() {
            return mType;
        }

        public SensorBuffer GetObs() {
            SensorBuffer buffer = new SensorBuffer(GetSize(), GetShape(), GetSensorType());
            GetState(buffer);
            return buffer;
        }

        public void GetState(SensorBuffer buffer) {
            for (int i = 0; i < raycastAngles.Count; i++) {
                var angleH = raycastAngles[i].horizontal;
                var angleV = raycastAngles[i].vertical;

                // transform the direction to the Actors frame of reference
                Vector3 raycastDir = Quaternion.AngleAxis(angleH, node.transform.up) *
                Quaternion.AngleAxis(angleV, node.transform.right) * node.transform.forward;
                RaycastHit raycastHit;
                var isHit = Physics.Raycast(node.transform.position, raycastDir, out raycastHit, rayLength); // TODO add Raycast layer mask?
                buffer.floatBuffer[i] = raycastDistance(raycastHit, isHit);
                if (true) { // TODO: remove this from release version
                    Debug.DrawRay(node.transform.position, rayLength * raycastDir.normalized);
                }
            }
        }

        private float raycastDistance(RaycastHit raycastHit, bool isHit) {
            // normalizes the result to range 0-1
            if (isHit) {
                return 1.0f - raycastHit.distance / rayLength;
            }
            return 0.0f;
        }

        public void Enable() { }
        public void Disable() { }
    }
}