
class CanoeApi:
    def __init__(self):
        self.app = None
        self.name: str = "James"
        
    def get_sys_var(self, namespace: str, var_name: str):
        """读取CANoe系统变量"""
        systemCAN = self.app.System.Namespaces
        sys_namespace = systemCAN(namespace)
        sys_value = sys_namespace.Variables(var_name)
        return sys_value.Value
        
    def set_sys_var(self, namespace: str, var_name: str, value):
        if(self.app != None):
        
            """设置CANoe系统变量"""
            systemCAN = self.app.System.Namespaces
            sys_namespace = systemCAN(namespace)
            sys_value = sys_namespace.Variables(var_name)
            sys_value.Value = value
        else:
            raise RuntimeError("CANoe is not open, unable to GetVariable.");
 
    def set_signal(self, sig_name: str, db_name: str, value):
        """设置CAN信号值"""
        sig = self.app.GetSignal(sig_name, db_name)
        sig.Value = value