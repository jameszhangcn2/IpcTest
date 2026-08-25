import cv2
import datetime
import os
import numpy as np
from skimage.metrics import structural_similarity



def find_hmi_screen_rect(img, case_dir, blur_ksize=5, canny_low=20, canny_high=90):
    height, width = img.shape[:2]
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    blur = cv2.GaussianBlur(gray, (blur_ksize, blur_ksize), 0)
    edges = cv2.Canny(blur, canny_low, canny_high)
    kernel = np.ones((9, 9), np.uint8)
    edges_dilate = cv2.dilate(edges, kernel, iterations=2)
    
    
    # =========调试：保存中间图，看边缘=========
    temp_path = os.path.join(case_dir, "debug_gray.jpg")
    cv2.imwrite(temp_path, gray)
    temp_path = os.path.join(case_dir, "debug_edges.jpg")
    cv2.imwrite(temp_path, edges)
    temp_path = os.path.join(case_dir, "debug_edges_dilate.jpg")
    cv2.imwrite(temp_path, edges_dilate)
    # ========================================
    
    contours, _ = cv2.findContours(edges_dilate, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    contours = sorted(contours, key=cv2.contourArea, reverse=True)
    screen_corners = None
    for cnt in contours:
        area = cv2.contourArea(cnt)
        if area < height * width * 0.04:
            continue
        peri = cv2.arcLength(cnt, True)
        approx = cv2.approxPolyDP(cnt, 0.03 * peri, True)
        if len(approx) == 4:
            screen_corners = approx.reshape((4, 2))
            break
    return screen_corners

def order_corners(pts):
    rect = np.zeros((4, 2), dtype="float32")
    s = pts.sum(axis=1)
    rect[0] = pts[np.argmin(s)]
    rect[2] = pts[np.argmax(s)]
    diff = np.diff(pts, axis=1)
    rect[1] = pts[np.argmin(diff)]
    rect[3] = pts[np.argmax(diff)]
    return rect

def expand_corners(pts, expand_ratio=0.05):
    """
    四边形角点向外等比例扩张
    :param pts: 4个角点 (4,2)
    :param expand_ratio: 向外扩张比例，0.05代表向外扩展屏幕尺寸5%；如果需要固定像素可改版本
    :return: 扩张后新4角点
    """
    pts = pts.astype(np.float32)
    # 中心点
    center = np.mean(pts, axis=0)
    new_pts = []
    for p in pts:
        # 从中心指向角点的向量，向外拉长
        vec = p - center
        new_p = center + vec * (1.0 + expand_ratio)
        new_pts.append(new_p)
    return np.array(new_pts, dtype=np.float32)

def warp_hmi_with_margin(img, corners, fixed_width=1280, expand_ratio=0.05):
    """
    HMI透视矫正，角点向外扩展保留四周轮廓边距，固定输出宽度，高度随比例自适应
    :param img: 原始BGR图像
    :param corners: 检测到屏幕四角
    :param fixed_width: 输出固定横向宽度
    :param expand_ratio: 向外扩张比例 0.0~0.1，0.05=向外扩展5%屏幕大小
    :return: warped图像，包含HMI+四周扩展余量
    """
    rect = order_corners(corners)
    # 角点向外扩张
    expanded_rect = expand_corners(rect, expand_ratio=expand_ratio)

    (tl, tr, br, bl) = expanded_rect
    maxWidth = max(np.sqrt(((br[0] - bl[0]) ** 2) + ((br[1] - bl[1]) ** 2)),
                   np.sqrt(((tr[0] - tl[0]) ** 2) + ((tr[1] - tl[1]) ** 2)))
    maxHeight = max(np.sqrt(((tr[0] - br[0]) ** 2) + ((tr[1] - br[1]) ** 2)),
                    np.sqrt(((tl[0] - bl[0]) ** 2) + ((tl[1] - bl[1]) ** 2)))

    ratio = maxHeight / maxWidth
    out_w = fixed_width
    out_h = int(fixed_width * ratio)

    dst = np.array([
        [0, 0],
        [out_w - 1, 0],
        [out_w - 1, out_h - 1],
        [0, out_h - 1]
    ], dtype="float32")

    M = cv2.getPerspectiveTransform(expanded_rect, dst)
    warped = cv2.warpPerspective(img, M, (out_w, out_h))
    return warped

def add_padding_after_warp(img, pad_left, pad_right, pad_top, pad_bottom):
    """
    方式2：矫正完成之后，图片四周补黑边（仅画布填充，不是真实图像内容）
    """
    return cv2.copyMakeBorder(img, pad_top, pad_bottom, pad_left, pad_right, cv2.BORDER_CONSTANT, value=(0,0,0))


class CameraPicture:
    def __init__(self, camera_id: int = 0):
        self.camera_id = camera_id
    def camera_save_pic(self, frame,case_dir, filename):
        save_path = os.path.join(case_dir, filename)
        print("Pic save path: ", save_path)
        cv2.imwrite(save_path, frame)

    # ==========OpenCV工具函数：摄像头截图、SSIM比对==========
    def camera_capture_one(self, width=1280, height=720, case_dir: str = "", filename: str = "testpic"):
        cap = cv2.VideoCapture(self.camera_id)
        cap.set(cv2.CAP_PROP_FRAME_WIDTH, width)
        cap.set(cv2.CAP_PROP_FRAME_HEIGHT, height)
        for _ in range(5):
            cap.read()
        ret, frame = cap.read()
        cap.release()
        if not ret:
            return None
        self.camera_save_pic(frame, case_dir, filename)
        return frame
     
    def camera_uniform_pic(self, pic_path, case_dir, out_filename):
        input_path = os.path.join(case_dir, pic_path)
        save_path = os.path.join(case_dir, out_filename)
        print("Pic save path: ", save_path)
        img = cv2.imread(input_path)
        corners = find_hmi_screen_rect(img, case_dir, blur_ksize=7, canny_low=20, canny_high=90)
        if corners is None:
            print("未识别HMI屏幕")
        else:
            # 透视前角点向外扩展5%，保留四周轮廓
            out1 = warp_hmi_with_margin(img, corners, fixed_width=1280, expand_ratio=0.3)
            print(f"角点外扩输出尺寸 w={out1.shape[1]},h={out1.shape[0]}")
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
        
        