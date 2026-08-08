# IpcTest
Automative test for DESAY SV IPC 7 inch

## CAPL and Python call each other, COM 
### 使用pytest+allure+CANoe组合框架实现诊断自动化测试

```
pytest 调用 CANoe（COM接口）
原理：pytest的 fixture 管理CANoe生命周期，通过 win32com.client 调用CANoe COM接口，打开cfg工程、启停测量、读写信号/系统变量，同时可以混入OpenCV做HMI视觉校验。
仅支持Windows，CANoe软件必须预先安装授权。
安装依赖
bash   
pip install pytest pywin32 opencv-python scikit‑image allure‑pytest

```
