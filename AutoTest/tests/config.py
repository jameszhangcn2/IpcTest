from pathlib import Path

CAMERA_INDEX_PICTURE = 0   # 第0号摄像头，多摄像头可改成1,2
CAMERA_INDEX_VIDEO = 2
REC_FPS = 12
KL15COM_PORT="COM6"

BASE_DIR = Path(__file__).resolve().parent

CANOE_CFG = str(BASE_DIR / "CANoe" / "test.cfg")# CANoe工程cfg绝对路径
 
TEMPLATE_HOMEPAGE_IMG = str(BASE_DIR / ".." / "testTemplate" / "home0.png") # HMI局域匹配模板图
TEMPLATE_ODOMETER_IMG = str(BASE_DIR / ".." / "testTemplate" / "odometer.png") # HMI局域匹配模板图
TEMPLATE_SPEEDOMETER_IMG = str(BASE_DIR / ".." / "testTemplate" / "speedometer.png") # HMI局域匹配模板图
TEMPLATE_TRIPSUMMAR_IMG = str(BASE_DIR / ".." / "testTemplate" / "tripsummary.png") # HMI局域匹配模板图
TEMPLATE_SUMMARY_IMG = str(BASE_DIR / ".." / "testTemplate" / "summary.png") # HMI参考模板图

CAP_HOME_PAGE_IMG = "cap_home_page.png"  
CAP_SUMMARY_IMG = "cap_summary.png"
CAP_HOME_PAGE_IMG = "cap_home_page.png"

PAGE_HOME_SUBMENU_TABLE = [
    {"sub_menu_name": "home_01",      "id_pictures":[{"path":TEMPLATE_SPEEDOMETER_IMG, "roi":(620, 256, 140, 171), "score":0.6},]},
    {"sub_menu_name": "home_02",      "id_pictures":[{"path":TEMPLATE_ODOMETER_IMG, "roi":(400, 250, 300, 200), "score":0.6},
                                                     {"path":TEMPLATE_SPEEDOMETER_IMG, "roi":(400, 250, 300, 200), "score":0.7},]},
]

PAGE_SETTING_SUBMENU_TABLE = [
    {"sub_menu_name": "setting_01",   "id_pictures":[{"path":TEMPLATE_SUMMARY_IMG, "roi":(200, 150, 700, 450), "score":0.6},
                                                     {"path":TEMPLATE_SUMMARY_IMG, "roi":(200, 150, 700, 450), "score":0.6},]},
]

PAGE_TABLE = [
    {"page_name": "HOME",          "sub_menus":PAGE_HOME_SUBMENU_TABLE},
    {"page_name": "SETTING",       "sub_menus":PAGE_SETTING_SUBMENU_TABLE},
    {"page_name": "MESSAGES",      "sub_menus":PAGE_SETTING_SUBMENU_TABLE},
    {"page_name": "MUSIC",         "sub_menus":PAGE_SETTING_SUBMENU_TABLE},
    {"page_name": "VEHICLE",       "sub_menus":PAGE_SETTING_SUBMENU_TABLE},
    {"page_name": "ACC",           "sub_menus":PAGE_SETTING_SUBMENU_TABLE},
    {"page_name": "TRIP",          "sub_menus":PAGE_SETTING_SUBMENU_TABLE},
]

