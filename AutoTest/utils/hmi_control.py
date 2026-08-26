import time
from pathlib import Path
from utils.image_check import template_match_in_roi 
from tests.config import PAGE_TABLE, PAGE_HOME_SUBMENU_TABLE, TEMPLATE_SPEEDOMETER_IMG, CAMERA_INDEX_PICTURE
import logging

logger = logging.getLogger(__name__)

def find_first(records:list[dict], key, match_value):
    for row in records:
        if row.get(key) == match_value:
            return row
    return None

def finding_home_page(canoe_api, cam_picture, case_logger_dir, timeout:float=10.0, sleep_step:float=0.5):

    start = time.time()
    loop = 0
    while time.time() - start < timeout:
        ok = False
        
        tempPic = f"temp_{loop}.png"
        cam_picture.camera_capture_one(1280, 720, case_logger_dir, tempPic)
        roi = (400, 250, 300, 200)
        big_img_path = str(Path(case_logger_dir) / tempPic)
        
        #check odometer match
        exists, score, pos = template_match_in_roi(big_img_path, SPEEDOMETER_IMG, roi, threshold=0.8)
        logger.info(f"Match odometer points: {score:.3f}")
        loop+=1
        if exists:
            ok = True
            logger.info(f"We found the home page.: {score:.3f}")
        
        if ok:
            return True
        time.sleep(sleep_step)
        ButtonLeftState = canoe_api.get_sys_var("Sysv_SWC", "Sysv_SWC_LEFT")
        #logger.info(f"ButtonLeftState {ButtonLeftState}")
        canoe_api.set_sys_var("Sysv_SWC", "Sysv_SWC_LEFT", 1)
        ButtonLeftState = canoe_api.get_sys_var("Sysv_SWC", "Sysv_SWC_LEFT")
        logger.info(f"ButtonLeftState {ButtonLeftState}")
        time.sleep(0.2) 
        canoe_api.set_sys_var("Sysv_SWC", "Sysv_SWC_LEFT", 0)
        ButtonLeftState = canoe_api.get_sys_var("Sysv_SWC", "Sysv_SWC_LEFT")
        #logger.info(f"ButtonLeftState {ButtonLeftState}")
        time.sleep(2)
        
    # 超时退出
    return False
def is_page_has_sub_menu(page_name):
    if page_name == None:
        #if None page name, default there is submenu
        return True;
    page = find_first(PAGE_TABLE, "page_name", page_name)
    logger.info(f"find page {page_name} {page}")
    if len(page["sub_menus"]):
        return True
    return False

    
def get_current_page(cap_picture_path):
    valid = False
    page_name = None
    sub_menu_name = None
    
    start = time.time()
    loop = 0
    
    page_num = len(PAGE_TABLE)
    logger.info("Total Page num %d",page_num)
    for i in range(page_num):
        logger.info("page table loop %d.", i)
        sub_menus = PAGE_TABLE[i]["sub_menus"]
        sub_menu_num = len(sub_menus)
        logger.info("sub_menu_num %d.",sub_menu_num)
        for j in range(sub_menu_num):
            logger.info("sub menu loop %d", j)
            id_pictures = sub_menus[j]["id_pictures"]
            id_picture_num = len(id_pictures)
            logger.info(" id_picture_num %d",id_picture_num)
            all_id_pic_match = True
            for k in range(id_picture_num):
                logger.info("id_picture loop %d", k)
                exists, score, pos = template_match_in_roi(cap_picture_path, id_pictures[k]["path"], id_pictures[k]["roi"], id_pictures[k]["score"])
                logger.info("Try to match %s %s %s", PAGE_TABLE[i]["page_name"], sub_menus[j]["sub_menu_name"], id_pictures[k]["path"])
                loop+=1
                logger.info(f"Pic match result {exists} {score} {pos}")
                if not exists:
                    all_id_pic_match = False
                    logger.info(f"Pic not match.: {score:.3f}")
            if all_id_pic_match:
                logger.info("All ID pictures match.")
                return True,PAGE_TABLE[i]["page_name"],sub_menus[j]["sub_menu_name"]

    return     False, None, None   

def ring_dir_calc(a:int, b:int, n:int=10):
    """
    :param a:起点
    :param b:终点
    :param n:环总点数
    :return: clockwise(顺步数), counter(逆步数), min_dist, direction
        direction: "clockwise" / "counter" / "equal"
    """
    if a == b:
        return 0, 0, 0, "equal"

    if b >= a:
        clockwise = b - a
    else:
        clockwise = (n - a) + b

    counter = n - clockwise
    min_dist = min(clockwise, counter)

    if clockwise < counter:
        direct = "clockwise"
    elif counter < clockwise:
        direct = "counter"
    else:
        direct = "equal"  # 两边距离相等

    return clockwise, counter, min_dist, direct
    
def left_button(canoe_api):
    ButtonLeftState = canoe_api.get_sys_var("Sysv_SWC", "Sysv_SWC_LEFT")
    #logger.info(f"ButtonLeftState {ButtonLeftState}")
    canoe_api.set_sys_var("Sysv_SWC", "Sysv_SWC_LEFT", 1)
    ButtonLeftState = canoe_api.get_sys_var("Sysv_SWC", "Sysv_SWC_LEFT")
    #logger.info(f"ButtonLeftState {ButtonLeftState}")
    time.sleep(0.2) 
    canoe_api.set_sys_var("Sysv_SWC", "Sysv_SWC_LEFT", 0)
    ButtonLeftState = canoe_api.get_sys_var("Sysv_SWC", "Sysv_SWC_LEFT")
    #logger.info(f"ButtonLeftState {ButtonLeftState}")
    logger.info(f"Left button. {ButtonLeftState}")

def right_button(canoe_api):
    ButtonRightState = canoe_api.get_sys_var("Sysv_SWC", "Sysv_SWC_RIGHT")
    #logger.info("f ButtonRightState {ButtonLeftState}")
    canoe_api.set_sys_var("Sysv_SWC", "Sysv_SWC_RIGHT", 1)
    ButtonRightState = canoe_api.get_sys_var("Sysv_SWC", "Sysv_SWC_RIGHT")
    #logger.info("f ButtonRightState {ButtonLeftState}")
    time.sleep(0.2) 
    canoe_api.set_sys_var("Sysv_SWC", "Sysv_SWC_RIGHT", 0)
    ButtonRightState = canoe_api.get_sys_var("Sysv_SWC", "Sysv_SWC_RIGHT")
    #logger.info("f ButtonRightState {ButtonLeftState}")
    logger.info(f"Right button. {ButtonRightState}")
    
def down_button(canoe_api):
    ButtonDownState = canoe_api.get_sys_var("Sysv_SWC", "Sysv_SWC_DOWN")
    logger.info(f"ButtonDownState {ButtonDownState}")
    canoe_api.set_sys_var("Sysv_SWC", "Sysv_SWC_DOWN", 1)
    ButtonDownState = canoe_api.get_sys_var("Sysv_SWC", "Sysv_SWC_DOWN")
    logger.info(f"ButtonDownState {ButtonDownState}")
    time.sleep(0.2) 
    canoe_api.set_sys_var("Sysv_SWC", "Sysv_SWC_DOWN", 0)
    ButtonDownState = canoe_api.get_sys_var("Sysv_SWC", "Sysv_SWC_DOWN")
    logger.info(f"ButtonDownState {ButtonDownState}")
    logger.info(f"Down button. {ButtonDownState}")
    
def go_to_page(page_name, sub_menu_name, canoe_api, cam_picture, case_logger_dir, timeout:float=10.0, sleep_step:float=0.5):

    start = time.time()
    loop = 0
    logger.info(" go_to_page Temp Loop %d page_name %s, sub_menu_name %s, cam_picture %s ", loop, page_name, sub_menu_name, cam_picture)
    down_button_count = 0
    left_button_count = 0    
    while time.time() - start < timeout:
        ok = False
        
        tempPic = f"temp_page_{loop}.png"
        tempUniformPic = f"temp_page_{loop}_uniformd.png"
        cam_picture.camera_capture_one(case_logger_dir, tempPic)
        ret = cam_picture.camera_uniform_pic(tempPic, case_logger_dir, tempUniformPic)
        current_page_name = None
        current_sub_menu_name = None
        big_img_path = None
        valid = False
        if ret:
            big_img_path = str(Path(case_logger_dir) / tempUniformPic)
            valid, current_page_name, current_sub_menu_name = get_current_page(big_img_path)
        logger.info("go_to_page Temp Loop %d valid %d, current_page_name %s, current_sub_menu_name %s ", loop, valid, current_page_name, current_sub_menu_name)

        if is_page_has_sub_menu(current_page_name) and (down_button_count < 10) and (current_page_name == page_name):
            if current_sub_menu_name == sub_menu_name:
                logger.info("We found the requested page: %s %s", page_name, sub_menu_name)
                return True
            else:
                down_button(canoe_api)
                down_button_count += 1
                    
        else:
            left_button(canoe_api)
            down_button_count = 0
            left_button_count += 1
        loop += 1
        logger.info("down_button_count %d , left_button_count %d ",down_button_count,left_button_count)
        time.sleep(6.0) #wait navigator bar disappear
        time.sleep(sleep_step)
    # wait time out
    return False
    
    
def show_all_pages(canoe_api, cam_picture, case_logger_dir, timeout:float=10.0, sleep_step:float=0.5):

    start = time.time()
    loop = 0
    
    while time.time() - start < timeout:
        ok = False
        for i in range(5):
            tempPic = f"page_{loop}_{i}.png"
            tempUniformPic = f"page_{loop}_{i}_uniformd.png"
            cam_picture.camera_capture_one(1280, 720, case_logger_dir, tempPic)
            cam_picture.camera_uniform_pic(tempPic, case_logger_dir, tempUniformPic)
            down_button(canoe_api)
            time.sleep(1.0)
            loop += 1
        left_button(canoe_api)
        time.sleep(sleep_step)
        
    # time out
    return False