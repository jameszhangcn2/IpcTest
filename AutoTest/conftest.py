# conftest.py
import pytest
from pathlib import Path
from utils.camera_recorder import CameraRecorder
from utils.camera_picture import CameraPicture
from utils.canoe_api import CanoeApi
from utils.serial_kl15 import SerialKL15

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
import sys
from datetime import datetime


BASE_DIR = Path(__file__).resolve().parent
VIDEO_DIR = BASE_DIR / "testlogs"
PICTURE_DIR = BASE_DIR / "testlogs"
CAMERA_INDEX_PICTURE = 0   # 第0号摄像头，多摄像头可改成1,2
CAMERA_INDEX_VIDEO = 2
REC_FPS = 12
KL15COM_PORT="COM6"
# ----------------------配置修改成你自己的路径----------------------
#CANOE_CFG = str(BASE_DIR / "CANoe" / "test.cfg")# CANoe工程cfg绝对路径
CANOE_CFG = str(BASE_DIR / "CANoe" / "332Replay.cfg")# CANoe工程cfg绝对路径
#TEMPLATE_IMG = str(BASE_DIR / "CANoe" / "demo.jpg") # HMI参考模板图
# ----------------------------------------------------------------

@pytest.fixture(scope="session")
def dir_session():
    log_dir = BASE_DIR / "testlogs/case_logs"
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    log_path = os.path.join(log_dir, f"{timestamp}")
    
    yield log_path
    
@pytest.fixture(scope="session")
def cam_recorder():
    rec = CameraRecorder(save_root=VIDEO_DIR, camera_id=CAMERA_INDEX_VIDEO)
    yield rec

@pytest.fixture(scope="session")
def cam_picture():
    rec = CameraPicture(save_root=PICTURE_DIR, camera_id=CAMERA_INDEX_PICTURE)
    yield rec
    
@pytest.fixture(scope="function", autouse=True)
def auto_camera_record(cam_recorder, request, case_logger_dir, case_logger):
    case_name = request.node.name
    stop_event = threading.Event()

    # 开启摄像头录像
    cam_recorder.start_record(case_name, case_logger_dir)

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
def canoe_api(kl15):
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
    kl15.kl15on() #keyon KL15
    time.sleep(2)
    # 显示 Configuration 视图
    #app.ActivateView(0)
    #app.ConfigurationWindow.Visible = True
        
    measurement = canoeApi.app.Measurement
 
    # 启动测量
    #if not measurement.Running:
    #    measurement.Start()
    #    time.sleep(2)
 
    yield canoeApi   # 把canoe对象传给测试用例
 
    # --------后置清理：全部用例跑完执行--------
    print("\n==== 关闭CANoe ====")
    if measurement.Running:
        measurement.Stop()
        kl15.kl15off() #keyon KL15
    canoeApi.app.Quit()
 

@pytest.fixture(scope="session")
def kl15():
    """
    session级别fixture：所有用例执行前启动CANoe，全部跑完关闭CANoe
    yield之前=前置；yield之后=后置清理，就算用例失败也执行
    """
    kl15 = SerialKL15(KL15COM_PORT)
    
    assert kl15.isKl15Open()
    time.sleep(2)
    
    yield kl15   # 把canoe对象传给测试用例
 
    # --------后置清理：全部用例跑完执行--------
    print("\n==== 关闭KL15 serial port ====")
    kl15.ser.close()
    

@pytest.fixture(scope="function")
def case_logger_dir(request, dir_session):
    # 获取当前用例完整名称，处理非法文件名字符
    case_name = request.node.nodeid.replace("/", "_").replace("\\", "_").replace(":", "_")
    log_dir = Path(dir_session)
    os.makedirs(log_dir, exist_ok=True)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    log_path = os.path.join(log_dir, f"{case_name}_{timestamp}")

    print(f"===== this case log dir：{log_path} =====")
    yield log_path
    print(f"===== this case log end：{log_path} =====")

@pytest.fixture(scope="function")
def case_logger(case_logger_dir, request):
    log_dir = Path(case_logger_dir)
    print("case_logger 文件夹是否存在：", log_dir.exists())
    os.makedirs(log_dir, exist_ok=True)
    time.sleep(1)
    print("case_logger 文件夹是否存在：", log_dir.exists())
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    log_path = os.path.join(case_logger_dir, f"ScriptLog_{timestamp}.log")
    log_fp = open(log_path, "w", encoding="utf-8")

    # 保存原始输出流
    old_stdout = sys.stdout
    old_stderr = sys.stderr

    class DualOutput:
        def write(self, text):
            old_stdout.write(text)
            log_fp.write(text)
            log_fp.flush()
        def flush(self):
            old_stdout.flush()

    stream = DualOutput()
    sys.stdout = stream
    sys.stderr = stream

    print(f"===== 测试用例开始：{request.node.nodeid} =====")
    yield log_path

    # 用例执行完成后恢复流，关闭文件
    print(f"===== 测试用例结束：{request.node.nodeid} =====")
    sys.stdout = old_stdout
    sys.stderr = old_stderr
    log_fp.close()
    print(f"本条用例日志已保存：{log_path}")
    