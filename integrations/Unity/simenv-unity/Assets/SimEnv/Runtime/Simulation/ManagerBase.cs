namespace SimEnv {
    public abstract class ManagerBase<Manager, Properties> : Singleton<Manager>
        where Manager : Singleton<Manager>
        where Properties : UnityEngine.ScriptableObject {

        public Properties m_properties;

        public abstract void InitializeProperties(Properties properties = null);
    }
}