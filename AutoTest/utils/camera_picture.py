import cv2
import datetime
import os
import numpy as np
from skimage.metrics import structural_similarity
from tests.config import CAMERA_PIC_WIDTH, CAMERA_PIC_HEIGHT, TEMPLATE_TRIPSUMMARY_ROI_IMG, ROI_SUMMARY_PAGE_SUMMARY, TEMPLATE_ODOMETER_IMG, ROI_HOME_PAGE_ODOMETER
from utils.image_check import template_match_in_roi, is_template_matched
import threading
import logging

logger = logging.getLogger(__name__)

class LatestFrameCapture:
    def __init__(self, src):
        self.cap = cv2.VideoCapture(src)
        self.cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)
        
        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, CAMERA_PIC_WIDTH)
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, CAMERA_PIC_HEIGHT)
        self.latest_frame = None
        self.ret = False
        self.running = True
        self.th = threading.Thread(target=self._loop, daemon=True)
        self.th.start()

    def _loop(self):
        while self.running:
            ret, frame = self.cap.read()
            if ret:
                self.ret = ret
                self.latest_frame = frame.copy()

    def get(self):
        return self.ret, self.latest_frame

    def release(self):
        self.running = False
        self.th.join()
        self.cap.release()

def find_hmi_screen_rect(img, case_dir, match_method, blur_ksize=5, canny_low=20, canny_high=90, area_min_ratio=0.04, poly_epsilon=0.03, dilate_kernel=9, dilate_iter=3):
    height, width = img.shape[:2]
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    blur = cv2.GaussianBlur(gray, (blur_ksize, blur_ksize), 0)
    edges = cv2.Canny(blur, canny_low, canny_high)
    kernel = np.ones((dilate_kernel, dilate_kernel), np.uint8)
    edges_dilate = cv2.dilate(edges, kernel, dilate_iter)
    
    
    # =========调试：保存中间图，看边缘=========
    temp_path = os.path.join(case_dir, f"debug_gray_{match_method}.jpg")
    cv2.imwrite(temp_path, gray)
    temp_path = os.path.join(case_dir, f"debug_edges_{match_method}.jpg")
    cv2.imwrite(temp_path, edges)
    temp_path = os.path.join(case_dir, f"debug_edges_dilate_{match_method}.jpg")
    cv2.imwrite(temp_path, edges_dilate)
    # ========================================
    
    contours, _ = cv2.findContours(edges_dilate, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    contours = sorted(contours, key=cv2.contourArea, reverse=True)
    screen_corners = None
    for cnt in contours:
        area = cv2.contourArea(cnt)
        if area < height * width * area_min_ratio:
            continue
        peri = cv2.arcLength(cnt, True)
        approx = cv2.approxPolyDP(cnt, poly_epsilon * peri, True)
        if len(approx) == 4:
            screen_corners = approx.reshape((4, 2))
            break
    return screen_corners

def order_corners(pts):
    """对4个点排序：左上，右上，右下，左下"""
    pts = pts.reshape((4,2))
    rect = np.zeros((4,2), dtype=np.float32)
    s = pts.sum(axis=1)
    rect[0] = pts[np.argmin(s)]   # 左上 sum最小
    rect[2] = pts[np.argmax(s)]   # 右下 sum最大
    diff = np.diff(pts, axis=1)
    rect[1] = pts[np.argmin(diff)]# 右上 diff最小
    rect[3] = pts[np.argmax(diff)]# 左下 diff最大
    return rect

def expand_rect_corners(rect, expand_px, img_w, img_h):
    """
    rect: 已经排序好的4角点 (4,2) float32
    expand_px: 四周向外扩多少像素（你要的轮廓边距）
    img_w,img_h:原图宽高，防止越界
    """
    # 拿到min/max x y
    x_coords = rect[:,0]
    y_coords = rect[:,1]
    x1 = max(0, np.min(x_coords) - expand_px)
    y1 = max(0, np.min(y_coords) - expand_px)
    x2 = min(img_w, np.max(x_coords) + expand_px)
    y2 = min(img_h, np.max(y_coords) + expand_px)
    # 生成新的规整四点
    new_rect = np.array([
        [x1, y1],
        [x2, y1],
        [x2, y2],
        [x1, y2]
    ], dtype=np.float32)
    return new_rect

def warp_hmi_with_margin(frame, corners, margin=20, canvas_w=1280, canvas_h=720):
    h, w = frame.shape[:2]
    # 1. 四点排序
    rect = order_corners(corners)
    # 2. 向外扩margin
    expanded_rect = expand_rect_corners(rect, margin, w, h)
    # 3. 目标画布四点
    dst = np.array([
        [0, 0],
        [canvas_w, 0],
        [canvas_w, canvas_h],
        [0, canvas_h]
    ], dtype=np.float32)
    # 4. 透视矩阵 + 变换
    M = cv2.getPerspectiveTransform(expanded_rect, dst)
    warped = cv2.warpPerspective(frame, M, (canvas_w, canvas_h))
    return warped

def add_padding_after_warp(img, pad_left, pad_right, pad_top, pad_bottom):
    """
    方式2：矫正完成之后，图片四周补黑边（仅画布填充，不是真实图像内容）
    """
    return cv2.copyMakeBorder(img, pad_top, pad_bottom, pad_left, pad_right, cv2.BORDER_CONSTANT, value=(0,0,0))

def is_summary_page_match(summary_img_path):
    found, max_val, match_method = is_template_matched(summary_img_path, TEMPLATE_TRIPSUMMARY_ROI_IMG, ROI_SUMMARY_PAGE_SUMMARY)
    return found, max_val
def is_odometer_page_match(home_img_path):
    found, max_val, match_method = is_template_matched(home_img_path, TEMPLATE_ODOMETER_IMG, ROI_HOME_PAGE_ODOMETER)
    return found, max_val

def remove_hmi_glare(img):
    # 1. LAB空间对亮度通道做CLAHE自适应增强，抑制高光
    lab = cv2.cvtColor(img, cv2.COLOR_BGR2LAB)
    l, a, b = cv2.split(lab)
    clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8,8))
    l_enh = clahe.apply(l)
    img_enh = cv2.merge((l_enh,a,b))
    img_enh = cv2.cvtColor(img_enh, cv2.COLOR_LAB2BGR)

    # 2. 高光抑制（gamma校正，压亮区）S
    gamma = 0.45
    look_up = np.array([((i / 255.0) ** gamma) * 255 for i in np.arange(0, 256)]).astype("uint8")
    img_gamma = cv2.LUT(img_enh, look_up)

    # 3. 可选：掩膜只处理HMI ROI区域，不影响背景
    return img_gamma    
    
class CameraPicture:
    def __init__(self, camera_id: int = 0):
        self.camera_id = camera_id
        self.cam = LatestFrameCapture(camera_id)

    def camera_save_pic(self, frame,case_dir, filename):
        save_path = os.path.join(case_dir, filename)
        logger.info("CAP Pic save path %s.", save_path)
        cv2.imwrite(save_path, frame)

    # ==========OpenCV工具函数：摄像头截图、SSIM比对==========
    def camera_capture_one(self, case_dir: str = "", filename: str = "testpic", width=CAMERA_PIC_WIDTH, height=CAMERA_PIC_HEIGHT):

        ret, frame = self.cam.get()

        if not ret:
            return None
        self.camera_save_pic(frame, case_dir, filename)
        return frame
     
    def camera_uniform_pic(self, pic_path, case_dir, out_filename):
        input_path = os.path.join(case_dir, pic_path)
        save_path = os.path.join(case_dir, out_filename)
        logger.info("Uniformed Pic save path %s.", save_path)
        img = cv2.imread(input_path)
        hmi_found = False
        corners = find_hmi_screen_rect(img, case_dir, "1", blur_ksize=5, canny_low=2, canny_high=20, area_min_ratio=0.04, poly_epsilon=0.03, dilate_kernel=9, dilate_iter=9)
        if corners is None:
            logger.info("Can not recognize the HMI with canny low 20.")
            corners = find_hmi_screen_rect(img, case_dir, "2",  blur_ksize=9, canny_low=15, canny_high=50)
            if corners is None:
                logger.info("Can not recognize the HMI with canny low 15.")
                corners = find_hmi_screen_rect(img, case_dir, "3",  blur_ksize=9, canny_low=8, canny_high=35)
                if corners is None:
                    logger.info("Can not recognize the HMI with canny low 8.")
                else:
                    hmi_found = True
            else:
                hmi_found = True
        else:
            hmi_found = True
        if hmi_found:
            # 透视前角点向外扩展5%，保留四周轮廓
            logger.info("HMI found!!")
            out1 = warp_hmi_with_margin(img, corners, margin=260)
            logger.info(f"out put size w={out1.shape[1]},h={out1.shape[0]}")
            cv2.imwrite(save_path, out1)
        return os.path.exists(save_path)
        
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
    

        