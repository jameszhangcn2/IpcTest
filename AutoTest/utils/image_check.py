import cv2
import numpy as np
import pyautogui
import time
from pathlib import Path
import logging
import os
from tests.config import ROI_PAGE_BIG, DEBUG_SAVE_EDGE, DEBUG_SAVE_DIR
logger = logging.getLogger(__name__)

def template_match_exist(big_img_path: str, template_path: str, threshold: float = 0.8):
    """
    :param big_img_path: 大图路径（截图）
    :param template_path: 待查找小图标模板
    :param threshold: 匹配阈值 0~1，越高越严格
    :return: (是否找到, 最大匹配值, 匹配坐标)
    """
    big = cv2.imread(big_img_path)
    templ = cv2.imread(template_path)

    if big is None or templ is None:
        raise FileNotFoundError("图片读取失败，请检查路径")

    result = cv2.matchTemplate(big, templ, cv2.TM_CCOEFF_NORMED)
    max_val = np.max(result)
    loc = np.where(result >= threshold)

    found = len(loc[0]) > 0
    return found, max_val, loc
    
def template_match_in_memory(screen_pil, template_path, threshold=0.8):
    screen_cv = cv2.cvtColor(np.array(screen_pil), cv2.COLOR_RGB2BGR)
    templ = cv2.imread(template_path)
    res = cv2.matchTemplate(screen_cv, templ, cv2.TM_CCOEFF_NORMED)
    max_val = np.max(res)
    found = max_val >= threshold
    return found, max_val
    
    
def template_match_in_roi(big_img_path, template_path, roi, threshold=0.8):
    """
    roi = (x, y, w, h) 只在这个矩形区域查找
    :return: (found:bool, max_score:float, pos|None)
    """
    big = cv2.imread(str(big_img_path))
    templ = cv2.imread(str(template_path))
    found = False
    max_val = 0.0
    match_pos = None
    

    # 捕获图片读取失败
    if big is None:
        raise FileNotFoundError(f"大图读取失败，路径：{big_img_path}")
    if templ is None:
        raise FileNotFoundError(f"模板读取失败，路径：{template_path}")

    x, y, w, h = roi
    img_h, img_w = big.shape[:2]
    x2 = x + w
    y2 = y + h
    # ROI越界校验
    if x < 0 or y < 0 or x2 > img_w or y2 > img_h:
        logger.warning(f"ROI越界！图像尺寸(w={img_w},h={img_h})，roi右下角({x2},{y2})")
        return found, max_val, match_pos
    roi_img = big[y:y+h, x:x+w]
    # 模板不能大于ROI
    th, tw = templ.shape[:2]
    rh, rw = roi_img.shape[:2]
    if tw > rw or th > rh:
        logger.warning(f"模板尺寸大于ROI！模板(w={tw},h={th}) ROI(w={rw},h={rh})")
        return found, max_val, match_pos
    res = cv2.matchTemplate(roi_img, templ, cv2.TM_CCOEFF_NORMED)
    max_val = float(np.max(res))
    found = max_val >= threshold

    match_pos = None
    if found:
        rx, ry = np.unravel_index(np.argmax(res), res.shape)[::-1]
        match_pos = (x + rx, y + ry)

    return found, max_val, match_pos

 #grey match
def get_edge(img):
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    clahe = cv2.createCLAHE(clipLimit=2.5, tileGridSize=(8,8))
    gray_enhance = clahe.apply(gray)
    blur = cv2.GaussianBlur(gray_enhance, (3, 3), 0)
    edge = cv2.Canny(blur, 30, 120)
    return gray, gray_enhance, blur, edge

def match_hmi_by_edge_roi(
    hmi_warped_frame,
    template_img,
    roi: tuple,
    thresh=0.7
):
    """
    蓝底白字专用ROI边缘匹配，带可关闭的批量debug图保存
    """
    if not isinstance(hmi_warped_frame, np.ndarray) or hmi_warped_frame.size == 0:
        logger.warning("hmi图像无效")
        return False, 0.0, None, 0, 0
    if not isinstance(template_img, np.ndarray) or template_img.size == 0:
        logger.warning("模板图像无效")
        return False, 0.0, None, 0, 0

    x1, y1, x2, y2 = roi
    h_img, w_img = hmi_warped_frame.shape[:2]
    x1 = max(0, int(x1))
    y1 = max(0, int(y1))
    x2 = min(w_img, int(x2))
    y2 = min(h_img, int(y2))
    if x2 <= x1 or y2 <= y1:
        logger.warning("ROI区域非法")
        return False, 0.0, None, 0, 0

    roi_img = hmi_warped_frame[y1:y2, x1:x2]
    gray_roi, gray_enhance_roi, blur_roi, roi_edge = get_edge(roi_img)
    gray_tpl, gray_enhance_tpl, blur_tpl, tpl_edge = get_edge(template_img)

    tpl_h, tpl_w = tpl_edge.shape[:2]
    roi_h, roi_w = roi_edge.shape[:2]
    if tpl_w > roi_w or tpl_h > roi_h:
        logger.warning("模板尺寸大于ROI")
        return False, 0.0, None, tpl_w, tpl_h

    res = cv2.matchTemplate(roi_edge, tpl_edge, cv2.TM_CCOEFF_NORMED)
    _, max_val, _, max_loc = cv2.minMaxLoc(res)

    global_loc = None
    if max_val >= thresh:
        global_loc = (x1 + max_loc[0], y1 + max_loc[1])

    # ========== 批量保存debug图（开关控制） ==========
    if DEBUG_SAVE_EDGE:
        if not os.path.exists(DEBUG_SAVE_DIR):
            os.makedirs(DEBUG_SAVE_DIR)
        import time
        timestamp = f"{time.time():.3f}".replace(".", "_")
        cv2.imwrite(os.path.join(DEBUG_SAVE_DIR, f"{timestamp}_01_roi_origin.jpg"), roi_img)
        cv2.imwrite(os.path.join(DEBUG_SAVE_DIR, f"{timestamp}_02_roi_edge.jpg"), roi_edge)
        cv2.imwrite(os.path.join(DEBUG_SAVE_DIR, f"{timestamp}_03_tpl_origin.jpg"), template_img)
        cv2.imwrite(os.path.join(DEBUG_SAVE_DIR, f"{timestamp}_04_tpl_edge.jpg"), tpl_edge)
        # 如果匹配成功，额外保存带框完整HMI图
        if global_loc is not None:
            dbg_full = hmi_warped_frame.copy()
            gx, gy = global_loc
            cv2.rectangle(dbg_full, (gx, gy), (gx + tpl_w, gy + tpl_h), (0,255,0), 2)
            cv2.imwrite(os.path.join(DEBUG_SAVE_DIR, f"{timestamp}_05_full_hmi_match.jpg"), dbg_full)
    # =================================================

    if max_val >= thresh:
        return True, max_val, global_loc, tpl_w, tpl_h
    else:
        return False, max_val, None, tpl_w, tpl_h

def match_hmi_orb(img, template, good_thresh=15, dist_thresh=40):
    """
    :param img: 矫正后的HMI画面 BGR
    :param template: 模板图片 BGR
    :param good_thresh: 最少需要多少个优质匹配点才算匹配成功
    :param dist_thresh: 匹配距离阈值，越小越严格
    :return: (is_match, good_match_count, matches, kp1, kp2)
    """
    orb = cv2.ORB_create(nfeatures=1500,
                         fastThreshold=8,   # 大幅降低，弱边缘也识别成特征
                         edgeThreshold=3)
    gray1 = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    gray2 = cv2.cvtColor(template, cv2.COLOR_BGR2GRAY)

    kp1, des1 = orb.detectAndCompute(gray1, None)
    kp2, des2 = orb.detectAndCompute(gray2, None)

    logger.info(f"kp1数量：{len(kp1) if kp1 else 0}, des1={des1 is not None}")
    logger.info(f"kp2数量：{len(kp2) if kp2 else 0}, des2={des2 is not None}")

    # 关键保护：特征描述子为空直接返回False
    if des1 is None or des2 is None:
        return False, 0, [], kp1, kp2

    bf = cv2.BFMatcher(cv2.NORM_HAMMING)
    matches = bf.match(des1, des2)
    # 按距离从小到大排序
    matches = sorted(matches, key=lambda x: x.distance)
    # 筛选优质匹配
    good_matches = [m for m in matches if m.distance < dist_thresh]

    is_match = len(good_matches) >= good_thresh
    return is_match, len(good_matches), good_matches, kp1, kp2

def match_hmi_orb_roi(img, template, roi, good_thresh=10, dist_thresh=50):
    x1, y1, x2, y2 = roi
    h, w = img.shape[:2]
    # 边界保护
    x1 = max(0, int(x1))
    y1 = max(0, int(y1))
    x2 = min(w, int(x2))
    y2 = min(h, int(y2))
    roi_img = img[y1:y2, x1:x2]
    return match_hmi_orb(roi_img, template, good_thresh, dist_thresh)

def match_hmi_by_edge(hmi_warped_frame, template_img, thresh=0.7):
    """只匹配轮廓内容，完全忽略颜色、亮度"""
    def get_edge(img):
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        blur = cv2.GaussianBlur(gray, (3,3), 0)
        edge = cv2.Canny(blur, 50, 150)
        return edge

    frame_edge = get_edge(hmi_warped_frame)
    tpl_edge = get_edge(template_img)
    tpl_h, tpl_w = tpl_edge.shape[:2]

    res = cv2.matchTemplate(frame_edge, tpl_edge, cv2.TM_CCOEFF_NORMED)
    min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(res)
    if max_val >= thresh:
        return True, max_val, max_loc, tpl_w, tpl_h
    return False, max_val, None, tpl_w, tpl_h

#use 4 methods to match the template
def is_template_matched(big_img, template_img, roi, threshhold=0.8):

    if not os.path.isfile(big_img):
        logger.error(f"big picture not exist：{big_img}")
        # 直接返回匹配失败
        return False, 0.0, None
    if not os.path.isfile(template_img):
        logger.error(f"template pic not exist：{big_img}")
        # 直接返回匹配失败
        return False, 0.0, None
    
    hmi_img = cv2.imread(big_img)
    tpl = cv2.imread(template_img)


    found, max_val, match_pos = template_match_in_roi(big_img, template_img, roi, threshhold)
    logger.info(f"match 区域匹配得分:{max_val:.3f}, result={found}")
    if found:
        return True, max_val, "roi_match"

    #与ROI不同，这里是左上，右下
    #(cx, cy, rw, rh) = ROI_PAGE_BIG
    (cx, cy, rw, rh) = roi
    x1 = cx
    y1 = cy
    x2 = cx + rw
    y2 = cy + rh
    roi_area = (x1,y1,x2,y2)
    is_match, score, pos, w, h = match_hmi_by_edge_roi(
        hmi_warped_frame=hmi_img,
        template_img=tpl,
        roi=roi_area,
        thresh=threshhold
    )

    logger.info(f"ROI区域匹配得分:{score:.3f}, result={is_match}")
    if is_match:
        # 可选：在完整HMI图上画框验证
        x1, y1 = pos
        x2 = x1 + w
        y2 = y1 + h
        cv2.rectangle(hmi_img, (x1, y1), (x2, y2), (0,255,0), 2)
        cv2.imwrite("debug_blue_text_match.png", hmi_img)
        return True, score, "roi_edge_match"


    is_match, cnt, good, kp1, kp2 = match_hmi_orb(hmi_img, tpl)
    dbg_img = cv2.drawMatches(hmi_img, kp1, tpl, kp2, good, None, flags=cv2.DrawMatchesFlags_NOT_DRAW_SINGLE_POINTS)
    cv2.imwrite("debug_orb_match.jpg", dbg_img)
    logger.info(f"ORB valid points:{cnt}, match={is_match}")
    if is_match:
        return True, cnt, "orb_match"

    is_match, max_val, max_loc, tpl_w, tpl_h = match_hmi_by_edge(hmi_img, tpl, threshhold)
    logger.info(f"edge points:{max_val}, match={is_match}")
    if is_match:
        return True, max_val, "edge_match"
    return False, 0.0, None
