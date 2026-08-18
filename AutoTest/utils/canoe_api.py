from pathlib import Path
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
        
    def set_logging_blf_path(self, blf_abs_path: str, logger_index:int=1):
        """
        修改Measurement Setup第N个Logging模块输出路径
        :param blf_abs_path: 完整绝对路径，必须 .blf/.asc
        :param logger_index: Measurement Setup第几个Logging，默认第一个
        """
        blf_path = Path(blf_abs_path)
        # 自动创建目录
        blf_path.parent.mkdir(parents=True, exist_ok=True)

        # 获取OnlineSetup里所有Logging
        logging_collection = self.app.Configuration.OnlineSetup.LoggingCollection
        logger = logging_collection.Item(logger_index)

        # 关键：FullName = 完整文件路径
        logger.FullName = str(blf_path)
        print(f"✅ CANoe Log路径已设置：{logger.FullName}")

        # 可选：启用Logging（如果未勾选Enable Logging）
        #logger.Enabled = True