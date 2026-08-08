

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


```
运行pytest命令
bash   
# 简单运行
pytest test_canoe_hmi.py -v

python -m pytest test_canoe_hmi.py -v
 
# 生成allure报告
pytest test_canoe_hmi.py -v --alluredir=allure-result
allure serve allure-result
 
fixture scope选择（非常关键）
-  scope="session" ：整个pytest会话，只打开一次CANoe，推荐，避免反复启动关闭CANoe，速度快
-  scope="module" ：每个py测试文件，启停一次CANoe
-  scope="function" ：每个测试用例都重启CANoe，很慢，一般不使用
COM常用操作速查表
python   
# 1.读写系统变量
canoe.SystemVariables.GetVariable("NS::Var").Value
 
# 2.读写DBC信号
canoe.GetSignal("SigName","DBName").Value
 
# 3.启停测量
canoe.Measurement.Start()
canoe.Measurement.Stop()
 
# 4.执行CANoe内置Test Module测试单元
test_module = canoe.TestModules.Item("MyTestModule")
test_module.Run()
 
踩坑重点
cfg路径必须绝对路径，相对路径经常加载失败。
COM调用时，CANoe不要手动打开多个实例；Dispatch会连接第一个

```
