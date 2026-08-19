import cv2
import numpy as np
import pyautogui
import time
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
CAP_HOME_PAGE_IMG = "cap_home_page.png"   
ODOMETER_IMG = str(BASE_DIR / ".." / "testTemplate" / "odometer.png") # HMI局域匹配模板图
SPEEDOMETER_IMG = str(BASE_DIR / ".." / "testTemplate" / "speedometer.png") # HMI局域匹配模板图

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
        raise ValueError(f"ROI越界！图像尺寸(w={img_w},h={img_h})，roi右下角({x2},{y2})")

    roi_img = big[y:y+h, x:x+w]
    # 模板不能大于ROI
    th, tw = templ.shape[:2]
    rh, rw = roi_img.shape[:2]
    if tw > rw or th > rh:
        raise ValueError(f"模板尺寸大于ROI！模板(w={tw},h={th}) ROI(w={rw},h={rh})")

    res = cv2.matchTemplate(roi_img, templ, cv2.TM_CCOEFF_NORMED)
    max_val = float(np.max(res))
    found = max_val >= threshold

    match_pos = None
    if found:
        rx, ry = np.unravel_index(np.argmax(res), res.shape)[::-1]
        match_pos = (x + rx, y + ry)

    return found, max_val, match_pos
    
    
def finding_home_page(canoe_api, cam_picture, case_logger_dir, timeout:float=10.0, sleep_step:float=0.5):

    start = time.time()
    loop = 0
    while time.time() - start < timeout:
        # =========业务逻辑=========
        ok = False
        
        # ok, score, pos = template_match_in_roi(...)
        # val = canoe_api.read_signal("BHCAN::xxx::sig")
        # if val == expect_val:
        #     ok = True
        # ==========================
        ButtonLeftState = canoe_api.get_sys_var("Sysv_SWC", "Sysv_SWC_LEFT")
        print("\n ButtonLeftState ", ButtonLeftState)
        canoe_api.set_sys_var("Sysv_SWC", "Sysv_SWC_LEFT", 1)
        ButtonLeftState = canoe_api.get_sys_var("Sysv_SWC", "Sysv_SWC_LEFT")
        print("\n ButtonLeftState ", ButtonLeftState)
        time.sleep(0.2) 
        canoe_api.set_sys_var("Sysv_SWC", "Sysv_SWC_LEFT", 0)
        ButtonLeftState = canoe_api.get_sys_var("Sysv_SWC", "Sysv_SWC_LEFT")
        print("\n ButtonLeftState ", ButtonLeftState)
        time.sleep(2)
        tempPic = f"temp_{loop}.png"
        cam_picture.camera_capture_one(1280, 720, case_logger_dir, tempPic)
        roi = (400, 250, 300, 200)
        big_img_path = str(Path(case_logger_dir) / tempPic)
        
        #check odometer match
        exists, score, pos = template_match_in_roi(big_img_path, SPEEDOMETER_IMG, roi, threshold=0.8)
        print(f"Match odometer points: {score:.3f}")
        loop+=1
        if exists:
            ok = True
            print(f"We found the home page.: {score:.3f}")
        
        if ok:
            return True
        time.sleep(sleep_step)
    # 超时退出
    return False
        
        