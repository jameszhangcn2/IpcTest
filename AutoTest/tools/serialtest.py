import serial
import time

# 配置串口
ser = serial.Serial(
    port="COM3",        # Windows端口，设备管理器查看
    baudrate=9600,
    bytesize=serial.EIGHTBITS,
    parity=serial.PARITY_NONE,
    stopbits=serial.STOPBITS_ONE,
    timeout=0.2
)

if ser.is_open:
    print("串口打开成功")

# 继电器1 开
cmd_on = bytes([0xA0, 0x01, 0x01, 0xA2])
ser.write(cmd_on)
print("发送打开指令:", cmd_on.hex())
time.sleep(1)

# 继电器1 关
cmd_off = bytes([0xA0, 0x01, 0x00, 0xA1])
ser.write(cmd_off)
print("发送关闭指令:", cmd_off.hex())

ser.close()