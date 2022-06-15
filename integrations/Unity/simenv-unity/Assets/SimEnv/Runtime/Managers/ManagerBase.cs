namespace SimEnv {
    public abstract class ManagerBase<Manager, Properties> : Singleton<Manager>
        where Manager : Singleton<Manager>
        where Properties : UnityEngine.ScriptableObject {

        public Properties m_properties;

        /// <summary>
        /// Initialize the manager with a Properties ScriptableObject.
        /// </summary>
        /// <param name="properties">Scriptable properties, stored in Resources/Properties.</param>
        public abstract void InitializeProperties(Properties properties = null);
    }
}