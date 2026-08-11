# conftest.py
import pytest
from pathlib import Path
from utils.camera_recorder import CameraRecorder
from utils.camera_picture import CameraPicture
from utils.canoe_api import CanoeApi
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

BASE_DIR = Path(__file__).resolve().parent
VIDEO_DIR = BASE_DIR / "camera_video"
CAMERA_INDEX_PICTURE = 1   # 第0号摄像头，多摄像头可改成1,2
CAMERA_INDEX_VIDEO = 1
REC_FPS = 12
# ----------------------配置修改成你自己的路径----------------------
CANOE_CFG = str(BASE_DIR / "CANoe" / "test.cfg")# CANoe工程cfg绝对路径

#TEMPLATE_IMG = str(BASE_DIR / "CANoe" / "demo.jpg") # HMI参考模板图
# ----------------------------------------------------------------

@pytest.fixture(scope="session")
def cam_recorder():
    rec = CameraRecorder(save_root=VIDEO_DIR, camera_id=CAMERA_INDEX_VIDEO)
    yield rec

@pytest.fixture(scope="session")
def cam_picture():
    rec = CameraPicture(camera_id=CAMERA_INDEX_PICTURE)
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


def kill_canoe_process():
    try:
        subprocess.run(["taskkill", "/F", "/IM", "CANoe64.exe"], capture_output=True, shell=False)
        time.sleep(1.5)
    except Exception:
        pass
        
@pytest.fixture(scope="session")
def canoe_api():
    """
    session级别fixture：所有用例执行前启动CANoe，全部跑完关闭CANoe
    yield之前=前置；yield之后=后置清理，就算用例失败也执行
    """
    canoeApi = CanoeApi()
    kill_canoe_process()
    time.sleep(5)
    print("\n==== 连接CANoe COM ====")
    canoeApi.app = win32com.client.Dispatch("CANoe.Application")
    canoeApi.app.Visible = True   # True显示CANoe窗口；False后台运行
    print("\n Current COM CANOE version:", canoeApi.app.version)
 
    assert os.path.exists(CANOE_CFG)
    time.sleep(2)
    
    # 打开工程配置
    canoeApi.app.Open(CANOE_CFG)
    # 确认已加载
    config = canoeApi.app.Configuration
    print(f"✅ 已加载配置: {config.Name}")  # 应该显示你工程里的配置名（如 Configuration 1）
    time.sleep(2)
    # 显示 Configuration 视图
    #app.ActivateView(0)
    #app.ConfigurationWindow.Visible = True
        
    measurement = canoeApi.app.Measurement
 
    # 启动测量
    if not measurement.Running:
        measurement.Start()
        time.sleep(2)
 
    yield canoeApi   # 把canoe对象传给测试用例
 
    # --------后置清理：全部用例跑完执行--------
    print("\n==== 关闭CANoe ====")
    if measurement.Running:
        measurement.Stop()
    canoeApi.app.Quit()
    