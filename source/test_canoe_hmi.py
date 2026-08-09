import pytest
import win32com.client
import time
import cv2
import numpy as np
from skimage.metrics import structural_similarity
 
# ----------------------配置修改成你自己的路径----------------------
CANOE_CFG = r"C:\STLA\AutoTest\test.cfg"  # CANoe工程cfg绝对路径
TEMPLATE_IMG = r"C:\STLA\AutoTest\demo.jpg"  # HMI参考模板图
# ----------------------------------------------------------------
 
@pytest.fixture(scope="session")
def canoe_app():
    """
    session级别fixture：所有用例执行前启动CANoe，全部跑完关闭CANoe
    yield之前=前置；yield之后=后置清理，就算用例失败也执行
    """
    print("\n==== 连接CANoe COM ====")
    app = win32com.client.Dispatch("CANoe.Application")
    app.Visible = True   # True显示CANoe窗口；False后台运行
    print("\n Current COM CANOE version:", app.version)
 
    # 打开工程配置
    app.Open(CANOE_CFG)
    # 确认已加载
    config = app.Configuration
    print(f"✅ 已加载配置: {config.Name}")  # 应该显示你工程里的配置名（如 Configuration 1）

    # 显示 Configuration 视图
    #app.ActivateView(0)
    #app.ConfigurationWindow.Visible = True
        
    measurement = app.Measurement
 
    # 启动测量
    if not measurement.Running:
        measurement.Start()
        time.sleep(2)
 
    yield app   # 把canoe对象传给测试用例
 
    # --------后置清理：全部用例跑完执行--------
    print("\n==== 关闭CANoe ====")
    if measurement.Running:
        measurement.Stop()
    app.Quit()
 
 
def get_sys_var(canoe, namespace: str, var_name: str):
    """读取CANoe系统变量"""
    var = canoe.SystemVariables.GetVariable(f"{namespace}::{var_name}")
    return var.Value
 
 
def set_sys_var(canoe, namespace: str, var_name: str, value):
    """设置CANoe系统变量"""
    var = canoe.SystemVariables.GetVariable(f"{namespace}::{var_name}")
    var.Value = value
 
 
def set_signal(canoe, sig_name: str, db_name: str, value):
    """设置CAN信号值"""
    sig = canoe.GetSignal(sig_name, db_name)
    sig.Value = value
 
 
# ==========OpenCV工具函数：摄像头截图、SSIM比对==========
def camera_capture_one(cam_id=0, width=1280, height=720):
    cap = cv2.VideoCapture(cam_id)
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, width)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, height)
    for _ in range(5):
        cap.read()
    ret, frame = cap.read()
    cap.release()
    if not ret:
        return None
    return frame
 
 
def calc_ssim_camera_vs_template(template_path):
    frame = camera_capture_one(0)
    template = cv2.imread(template_path)
    h, w = template.shape[:2]
    frame = cv2.resize(frame, (w, h))
    g1 = cv2.cvtColor(template, cv2.COLOR_BGR2GRAY)
    g2 = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    score, _ = structural_similarity(g1, g2, full=True)
    return round(score, 4)
 
 
# ----------------pytest测试用例----------------
def test_dashboard_hmi_visual(canoe_app):
    """
    测试流程：
    1. CANoe下发车速信号 80km/h
    2. 等待HMI屏幕刷新
    3. OpenCV摄像头采集仪表画面，和模板做SSIM比对
    4. 把SSIM结果写入CANoe系统变量
    5. pytest断言相似度阈值
    """
    canoe = canoe_app
    keyonState = get_sys_var(canoe, "Sysv_IGWorkCondition", "Sysv_IGWorkCondition")
    
    print("\n Sysv_IGWorkCondition ", keyonState)
    
    
    set_sys_var(canoe, "Sysv_IGWorkCondition", "Sysv_IGWorkCondition", 5)
    
    print("\n Sysv_IGWorkCondition ", get_sys_var(canoe, "Sysv_IGWorkCondition", "Sysv_IGWorkCondition"))
 
    # 1. 设置总线信号 VehicleSpeed=80
    # set_signal(canoe, "VehicleSpeed", "DemoDB", 80)
    time.sleep(10)  # 等待HMI界面刷新
 
    # 2. OpenCV摄像头视觉比对
    ssim_score = calc_ssim_camera_vs_template(TEMPLATE_IMG)
    print(f"SSIM相似度 = {ssim_score}")
 
    # 3. 将视觉结果回写给CANoe系统变量
    set_sys_var(canoe, "VisualTest", "SSIM_Result", ssim_score)
 
    # 4. pytest断言：相似度大于0.92才算PASS
    assert ssim_score >= 0.92, f"HMI界面校验失败，SSIM={ssim_score}"
