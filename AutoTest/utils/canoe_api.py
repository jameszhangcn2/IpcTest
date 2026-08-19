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
        
    def canoe_send_can_message(self, channel: int, msg_id: int, data: list):
        """
        发送CAN报文
        :param simulation: canoe_app.Simulation 对象
        :param channel: CAN通道号，1/2
        :param msg_id: 报文ID 十进制
        :param data: 8字节列表 [0x11,0x22,...]
        """
        bus_can = self.app.Bus("BHCAN")
        msg = bus_can.CreateMessage(channel, msg_id)
        msg = self.app.CAN.CreateMessage(channel, msg_id)
        msg.Data = data
        msg.Send()
        
    def canoe_get_signal_value(self, signal_name: str, bus: str="CAN"):
        """
        读取当前信号值（Measurement → Signal）
        :param signal_name: 信号全名，如 "CAN::EngineData::EngineSpeed"
        :return: float
        """
        sig = self.app.Measurement.Signal(signal_name)
        return sig.Value
        
        
    def canoe_wait_signal(self, sig_name, expect_value, timeout=2.0, sleep_dt=0.05):
        """
        等待信号等于期望值，超时抛出异常
        """
        import time
        start = time.time()
        while time.time() - start < timeout:
            val = canoe_get_signal_value(self.app, sig_name)
            if val == expect_value:
                return True, val
            time.sleep(sleep_dt)
        return False, val
        
