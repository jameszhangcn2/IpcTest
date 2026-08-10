import pytest
import pythoncom
import win32com.client
import time
import datetime
import cv2
import os
import subprocess
import numpy as np
from skimage.metrics import structural_similarity
 
# ----------------------配置修改成你自己的路径----------------------
CANOE_CFG = r"C:\STLA\AutoTest\test.cfg"  # CANoe工程cfg绝对路径
TEMPLATE_IMG = r"C:\STLA\AutoTest\demo.jpg"  # HMI参考模板图
# ----------------------------------------------------------------

def kill_canoe_process():
    try:
        subprocess.run(["taskkill", "/F", "/IM", "CANoe64.exe"], capture_output=True, shell=False)
        time.sleep(1.5)
    except Exception:
        pass
        
@pytest.fixture(scope="session")
def canoe_app():
    """
    session级别fixture：所有用例执行前启动CANoe，全部跑完关闭CANoe
    yield之前=前置；yield之后=后置清理，就算用例失败也执行
    """
    print("\n==== 连接CANoe COM ====")
    app = win32com.client.DispatchEx("CANoe.Application")
    app.Visible = True   # True显示CANoe窗口；False后台运行
    print("\n Current COM CANOE version:", app.version)
 
    assert os.path.exists(CANOE_CFG)
    kill_canoe_process()
    time.sleep(1.2)
    
    # 打开工程配置
    app.Open(CANOE_CFG)
    # 确认已加载
    config = app.Configuration
    print(f"✅ 已加载配置: {config.Name}")  # 应该显示你工程里的配置名（如 Configuration 1）
    time.sleep(1.2)
    # 显示 Configuration 视图
    #app.ActivateView(0)
    #app.ConfigurationWindow.Visible = True
        
    measurement = app.Measurement
 
    # 启动测量
    if not measurement.Running:
        measurement.Start()
        time.sleep(5)
 
    yield app   # 把canoe对象传给测试用例
 
    # --------后置清理：全部用例跑完执行--------
    print("\n==== 关闭CANoe ====")
    if measurement.Running:
        measurement.Stop()
    app.Quit()
 
 
def get_sys_var(canoe, namespace: str, var_name: str):
    """读取CANoe系统变量"""
    systemCAN = canoe.System.Namespaces
    sys_namespace = systemCAN(namespace)
    sys_value = sys_namespace.Variables(var_name)
    #var = canoe.SystemVariables.GetVariable(f"{namespace}::{var_name}")
    return sys_value.Value
 
 
def set_sys_var(canoe, namespace: str, var_name: str, value):
    if(canoe != None):
    
        """设置CANoe系统变量"""
        #var = canoe.SystemVariables.GetVariable(f"{namespace}::{var_name}")
        systemCAN = canoe.System.Namespaces
        sys_namespace = systemCAN(namespace)
        sys_value = sys_namespace.Variables(var_name)
        sys_value.Value = value
    else:
        raise RuntimeError("CANoe is not open, unable to GetVariable.");
 
def set_signal(canoe, sig_name: str, db_name: str, value):
    """设置CAN信号值"""
    sig = canoe.GetSignal(sig_name, db_name)
    sig.Value = value
 
def camera_save_pic(frame,note: str = ""):
    # 1. 生成时间字符串
    now = datetime.datetime.now()
    time_str = now.strftime("%Y%m%d_%H%M%S")

    # 2. 创建文件夹（按日期分文件夹，方便归档）
    date_folder = os.path.join(os.getcwd(), now.strftime("%Y%m%d"))
    os.makedirs(date_folder, exist_ok=True)

    # 3. 组装文件名
    if note:
        filename = f"{time_str}_{note}.png"
    else:
        filename = f"{time_str}.png"
    save_path = os.path.join(date_folder, filename)
    print("Pic save path: ", save_path)
    cv2.imwrite(save_path, frame)

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
    frame = camera_capture_one(1)
    template = cv2.imread(template_path)
    h, w = template.shape[:2]
    frame = cv2.resize(frame, (w, h))
    
    camera_save_pic(frame)
    
    g1 = cv2.cvtColor(template, cv2.COLOR_BGR2GRAY)
    g2 = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    score, _ = structural_similarity(g1, g2, full=True)
    return round(score, 4)
 
 
# ----------------pytest测试用例----------------
#def test_dashboard_hmi_visual(canoe_app):
def test_dashboard_hmi_visual():
    """
    测试流程：
    1. CANoe下发车速信号 80km/h
    2. 等待HMI屏幕刷新
    3. OpenCV摄像头采集仪表画面，和模板做SSIM比对
    4. 把SSIM结果写入CANoe系统变量
    5. pytest断言相似度阈值
    """
    #canoe = canoe_app
    #pythoncom.CoInitialize()
    canoe = None
    assert os.path.exists(CANOE_CFG)
    kill_canoe_process()
    
    try:
        canoe = win32com.client.DispatchEx("CANoe.Application")
        canoe.Visible = True
        time.sleep(1.2)

        canoe.Open(CANOE_CFG)
        time.sleep(10)
        
        # 确认已加载
        config = canoe.Configuration
        print(f"✅ 已加载配置: {config.Name}")  # 应该显示你工程里的配置名（如 Configuration 1）
        time.sleep(1.2)
        # 显示 Configuration 视图
        #app.ActivateView(0)
        #app.ConfigurationWindow.Visible = True
            
        measurement = canoe.Measurement
     
        # 启动测量
        if not measurement.Running:
            measurement.Start()
        
        keyonState = get_sys_var(canoe, "Sysv_IGWorkCondition", "Sysv_IGWorkCondition")
        
        print("\n Sysv_IGWorkCondition ", keyonState)
        
        
        set_sys_var(canoe, "Sysv_IGWorkCondition", "Sysv_IGWorkCondition", 5)
        time.sleep(1) 
        print("\n Sysv_IGWorkCondition ", get_sys_var(canoe, "Sysv_IGWorkCondition", "Sysv_IGWorkCondition"))
     
        # 1. 设置总线信号 VehicleSpeed=80
        # set_signal(canoe, "VehicleSpeed", "DemoDB", 80)
        time.sleep(10)  # 等待HMI界面刷新
     
        # 2. OpenCV摄像头视觉比对
        ssim_score = calc_ssim_camera_vs_template(TEMPLATE_IMG)
        print(f"SSIM相似度 = {ssim_score}")
     
        # 3. 将视觉结果回写给CANoe系统变量
        #set_sys_var(canoe, "VisualTest", "SSIM_Result", ssim_score)
        
        # keyoff
        set_sys_var(canoe, "Sysv_IGWorkCondition", "Sysv_IGWorkCondition", 1)
        time.sleep(1) 
     
        # 4. pytest断言：相似度大于0.92才算PASS
        assert ssim_score >= 0.92, f"HMI界面校验失败，SSIM={ssim_score}"
        
    except Exception as e:
        print(f"Error: {e}")
        raise
    finally:
        if canoe is not None:
             
            # --------后置清理：全部用例跑完执行--------
            print("\n==== 关闭CANoe ====")
            canoe.Quit()
        pythoncom.CoUninitialize()
        #kill_canoe_process()
        
        
