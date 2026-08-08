

## Test

```

完整示例代码（test_canoe_hmi.py）
包含：
 fixture ：session级别，整个pytest会话只启动一次CANoe，结束自动关闭
打开cfg工程、启动/停止measurement
设置信号、读系统变量
集成前面OpenCV摄像头截图+SSIM图像比对（HMI视觉测试）
pytest断言判定PASS/FAIL

```
