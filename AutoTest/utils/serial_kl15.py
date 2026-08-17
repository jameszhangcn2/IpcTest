import serial
import time

class SerialKL15:
    def __init__(self, com_port: string = "COM3"):
        self.ser = serial.Serial(port=com_port,        # Windows端口，设备管理器查看
        baudrate=9600,
        bytesize=serial.EIGHTBITS,
        parity=serial.PARITY_NONE,
        stopbits=serial.STOPBITS_ONE,
        timeout=0.2)

    def kl15on(self):
        # 继电器1 开
        cmd_on = bytes([0xA0, 0x01, 0x01, 0xA2])
        self.ser.write(cmd_on)
        print("发送打开指令:", cmd_on.hex())
        time.sleep(1)
        
    def kl15off(self):
        # 继电器1 关
        cmd_off = bytes([0xA0, 0x01, 0x00, 0xA1])
        self.ser.write(cmd_off)
        print("发送关闭指令:", cmd_off.hex())
        
    def isKl15Open(self):
        if self.ser.is_open:
            print("串口打开成功")
            return 1
        else: return 0
