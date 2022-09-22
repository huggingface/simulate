using System.Collections;
using System.Collections.Generic;
using UnityEngine;

namespace Simulate.RlAgents {
    public class MapPool : IEnumerable<Map> {
        Queue<Map> pool;

        public MapPool() {
            pool = new Queue<Map>();
        }

        public void Push(Map map) {
            Debug.Assert(!pool.Contains(map));
            map.SetActive(false);
            pool.Enqueue(map);
        }

        public Map Request() {
            if (pool.Count == 0) {
                Debug.LogWarning("Pool empty");
                return null;
            }
            Map map = pool.Dequeue();
            map.SetActive(true);
            return map;
        }

        public void Clear() {
            pool.Clear();
        }

        public IEnumerator<Map> GetEnumerator() {
            return pool.GetEnumerator();
        }

        IEnumerator IEnumerable.GetEnumerator() {
            return GetEnumerator();
        }
    }
}