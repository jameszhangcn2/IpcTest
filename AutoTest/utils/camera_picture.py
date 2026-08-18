import cv2
import datetime
import os
import numpy as np
from skimage.metrics import structural_similarity

class CameraPicture:
    def __init__(self, save_root: Path, camera_id: int = 0):
        self.camera_id = camera_id
        self.save_root = save_root
    def camera_save_pic(self, frame,case_dir, note: str = ""):
        # 1. 生成时间字符串
        now = datetime.datetime.now()
        time_str = now.strftime("%Y%m%d_%H%M%S")
        #os.makedirs(self.save_root, exist_ok=True)
        # 2. 创建文件夹（按日期分文件夹，方便归档）
        #date_folder = os.path.join(self.save_root, now.strftime("%Y%m%d"))
        #os.makedirs(date_folder, exist_ok=True)

        # 3. 组装文件名
        if note:
            filename = f"{time_str}_{note}.png"
        else:
            filename = f"{time_str}.png"
        save_path = os.path.join(case_dir, filename)
        print("Pic save path: ", save_path)
        cv2.imwrite(save_path, frame)

    # ==========OpenCV工具函数：摄像头截图、SSIM比对==========
    def camera_capture_one(self, width=1280, height=720):
        cap = cv2.VideoCapture(self.camera_id)
        cap.set(cv2.CAP_PROP_FRAME_WIDTH, width)
        cap.set(cv2.CAP_PROP_FRAME_HEIGHT, height)
        for _ in range(5):
            cap.read()
        ret, frame = cap.read()
        cap.release()
        if not ret:
            return None
        return frame
     
     
    def calc_ssim_camera_vs_template(self, template_path, case_dir):
        frame = self.camera_capture_one()
        template = cv2.imread(template_path)
        h, w = template.shape[:2]
        frame = cv2.resize(frame, (w, h))
        
        self.camera_save_pic(frame, case_dir)
        
        g1 = cv2.cvtColor(template, cv2.COLOR_BGR2GRAY)
        g2 = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        score, _ = structural_similarity(g1, g2, full=True)
        return round(score, 4)
        
        