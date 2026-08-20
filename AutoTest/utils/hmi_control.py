import time
from pathlib import Path
from utils.image_check import template_match_in_roi 
from tests.config import PAGE_TABLE, PAGE_HOME_SUBMENU_TABLE, SPEEDOMETER_IMG

def find_first(records:list[dict], key, match_value):
    for row in records:
        if row.get(key) == match_value:
            return row
    return None

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
        
    # 超时退出
    return False
    
def get_current_page(cap_picture_path):
    valid = False
    page_name = None
    sub_menu_name = None
    
    start = time.time()
    loop = 0
    
    page_num = len(PAGE_TABLE)
    print("Page num:",page_num)
    for i in range(page_num):
        print("\n page loop:", i)
        sub_menus = PAGE_TABLE[i]["sub_menus"]
        sub_menu_num = len(sub_menus)
        print("\n sub_menu_num :",sub_menu_num)
        for j in range(sub_menu_num):
            print("\n sub menu loop:", j)
            id_pictures = sub_menus[j]["id_pictures"]
            id_picture_num = len(id_pictures)
            print("\n id_picture_num :",id_picture_num)
            all_id_pic_match = True
            for k in range(id_picture_num):
                print("\n id_picture loop:", k)
                exists, score, pos = template_match_in_roi(cap_picture_path, id_pictures[k]["path"], id_pictures[k]["roi"], id_pictures[k]["score"])
                print("Try to match: ", PAGE_TABLE[i]["page_name"], sub_menus[j]["sub_menu_name"], id_pictures[k]["path"])
                loop+=1
                print("\n Pic match result: exists", exists, score, pos)
                if not exists:
                    all_id_pic_match = False
                    print(f"Pic not match.: {score:.3f}")
            if all_id_pic_match:
                print("All ID pictures match.")
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
    print("\n ButtonLeftState ", ButtonLeftState)
    canoe_api.set_sys_var("Sysv_SWC", "Sysv_SWC_LEFT", 1)
    ButtonLeftState = canoe_api.get_sys_var("Sysv_SWC", "Sysv_SWC_LEFT")
    print("\n ButtonLeftState ", ButtonLeftState)
    time.sleep(0.2) 
    canoe_api.set_sys_var("Sysv_SWC", "Sysv_SWC_LEFT", 0)
    ButtonLeftState = canoe_api.get_sys_var("Sysv_SWC", "Sysv_SWC_LEFT")
    print("\n ButtonLeftState ", ButtonLeftState)

def right_button(canoe_api):
    ButtonRightState = canoe_api.get_sys_var("Sysv_SWC", "Sysv_SWC_RIGHT")
    print("\n ButtonRightState ", ButtonLeftState)
    canoe_api.set_sys_var("Sysv_SWC", "Sysv_SWC_RIGHT", 1)
    ButtonRightState = canoe_api.get_sys_var("Sysv_SWC", "Sysv_SWC_RIGHT")
    print("\n ButtonRightState ", ButtonRightState)
    time.sleep(0.2) 
    canoe_api.set_sys_var("Sysv_SWC", "Sysv_SWC_RIGHT", 0)
    ButtonRightState = canoe_api.get_sys_var("Sysv_SWC", "Sysv_SWC_RIGHT")
    print("\n ButtonRightState ", ButtonRightState)
    
def down_button(canoe_api):
    ButtonDownState = canoe_api.get_sys_var("Sysv_SWC", "Sysv_SWC_DOWN")
    print("\n ButtonDownState ", ButtonDownState)
    canoe_api.set_sys_var("Sysv_SWC", "Sysv_SWC_DOWN", 1)
    ButtonDownState = canoe_api.get_sys_var("Sysv_SWC", "Sysv_SWC_DOWN")
    print("\n ButtonDownState ", ButtonDownState)
    time.sleep(0.2) 
    canoe_api.set_sys_var("Sysv_SWC", "Sysv_SWC_DOWN", 0)
    ButtonDownState = canoe_api.get_sys_var("Sysv_SWC", "Sysv_SWC_DOWN")
    print("\n ButtonDownState ", ButtonDownState)
    
def go_to_page(page_name, sub_menu_name, canoe_api, cam_picture, case_logger_dir, timeout:float=10.0, sleep_step:float=0.5):

    start = time.time()
    loop = 0
    
    while time.time() - start < timeout:
        # =========业务逻辑=========
        ok = False

        tempPic = f"temp_{loop}.png"
        cam_picture.camera_capture_one(1280, 720, case_logger_dir, tempPic)
        big_img_path = str(Path(case_logger_dir) / tempPic)
        valid, current_page_name, current_sub_menu_name = get_current_page(big_img_path)
        print("valid, current_page_name, current_sub_menu_name: ", valid, current_page_name, current_sub_menu_name)
        
        if current_page_name == page_name:
            if current_sub_menu_name == sub_menu_name:
                print("We found the requested page: ", page_name, sub_menu_name)
                return True
            else:
                down_button(canoe_api)
        else:
            left_button(canoe_api)
        loop += 1
        
        time.sleep(sleep_step)
    # 超时退出
    return False
    
    
def show_all_pages(canoe_api, cam_picture, case_logger_dir, timeout:float=10.0, sleep_step:float=0.5):

    start = time.time()
    loop = 0
    
    while time.time() - start < timeout:
        # =========业务逻辑=========
        ok = False
        for i in range(5):
            tempPic = f"page_{loop}.png"
            cam_picture.camera_capture_one(1280, 720, case_logger_dir, tempPic)
            down_button(canoe_api)
            loop += 1
        left_button(canoe_api)
        time.sleep(sleep_step)
        
    # 超时退出
    return False