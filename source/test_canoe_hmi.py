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
from pathlib import Path
from typing import Optional
import threading
#from camera_recorder import CameraRecorder
 
# ----------------------配置修改成你自己的路径----------------------
CANOE_CFG = r"C:\STLA\AutoTest\test.cfg"  # CANoe工程cfg绝对路径
TEMPLATE_IMG = r"C:\STLA\AutoTest\demo.jpg"  # HMI参考模板图
# ----------------------------------------------------------------


class CameraRecorder:
    def __init__(self, save_root: Path, fps: int = 15, camera_id: int = 0):
        self.save_root = save_root
        self.fps = fps
        self.camera_id = camera_id
        self.cap: Optional[cv2.VideoCapture] = None
        self.writer: Optional[cv2.VideoWriter] = None
        self.video_path: str = ""

    def start_record(self, case_name: str):
        """启动摄像头+录像"""
        # 打开摄像头
        self.cap = cv2.VideoCapture(self.camera_id)
        if not self.cap.isOpened():
            raise RuntimeError(f"无法打开摄像头 id={self.camera_id}")

        # 获取摄像头分辨率
        width = int(self.cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        height = int(self.cap.get(cv2.CAP_PROP_FRAME_HEIGHT))

        # 路径构造
        time_str = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        date_folder = self.save_root / datetime.datetime.now().strftime("%Y%m%d")
        date_folder.mkdir(parents=True, exist_ok=True)
        self.video_path = str(date_folder / f"{time_str}_{case_name}.mp4")

        fourcc = cv2.VideoWriter_fourcc(*"mp4v")
        self.writer = cv2.VideoWriter(self.video_path, fourcc, self.fps, (width, height))
        print(f"[Camera Record START] {self.video_path}")

    def grab_frame(self):
        """读取一帧写入视频（子线程循环调用）"""
        if self.cap is None or self.writer is None:
            return
        ret, frame = self.cap.read()
        if ret:
            self.writer.write(frame)

    def stop_record(self):
        """释放摄像头、保存文件"""
        if self.writer:
            self.writer.release()
        if self.cap:
            self.cap.release()
        print(f"[Camera Record SAVED] {self.video_path}")
        self.writer = None
        self.cap = None
        
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
 
# =========配置区=========
BASE_PATH = Path(__file__).resolve().parent
VIDEO_DIR = BASE_PATH / "camera_video"
CAMERA_INDEX_PIC = 1   # 第0号摄像头，多摄像头可改成1,2
CAMERA_INDEX_VIDEO = 1
REC_FPS = 12
# =======================

@pytest.fixture(scope="session")
def cam_recorder():
    rec = CameraRecorder(save_root=VIDEO_DIR, fps=REC_FPS, camera_id=CAMERA_INDEX_VIDEO)
    yield rec

@pytest.fixture(scope="function", autouse=True)
def auto_camera_record(cam_recorder, request):
    case_name = request.node.name
    stop_event = threading.Event()

    # 开启摄像头录像
    cam_recorder.start_record(case_name)

    # 后台线程持续取帧
    def frame_loop():
        interval = 1.0 / cam_recorder.fps
        while not stop_event.is_set():
            cam_recorder.grab_frame()
            time.sleep(interval)

    rec_thread = threading.Thread(target=frame_loop, daemon=True)
    rec_thread.start()

    yield  # 执行测试用例

    # 用例结束，停止录制
    stop_event.set()
    rec_thread.join()
    cam_recorder.stop_record()


# =========可选：只失败保留视频，成功删除=========
@pytest.hookimpl(tryfirst=True, hookwrapper=True)
def pytest_runtest_makereport(item, call):
    outcome = yield
    rep = outcome.get_result()
    setattr(item, "rep_" + rep.when, rep)
    
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
    frame = camera_capture_one(CAMERA_INDEX_PIC)
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
        
        
