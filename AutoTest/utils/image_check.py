import cv2
import numpy as np
import pyautogui
    
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
    """
    big = cv2.imread(big_img_path)
    x, y, w, h = roi
    roi_img = big[y:y+h, x:x+w]
    templ = cv2.imread(template_path)
    res = cv2.matchTemplate(roi_img, templ, cv2.TM_CCOEFF_NORMED)
    max_val = np.max(res)
    return max_val >= threshold, max_val