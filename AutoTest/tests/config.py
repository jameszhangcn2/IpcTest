from pathlib import Path

CAMERA_INDEX_PICTURE = 2   # 第0号摄像头，多摄像头可改成1,2
CAMERA_INDEX_VIDEO = 1
CAMERA_PIC_WIDTH = 1920
CAMERA_PIC_HEIGHT = 1080
REC_FPS = 12
KL15COM_PORT="COM6"

BASE_DIR = Path(__file__).resolve().parent

CANOE_CFG = str(BASE_DIR / ".." / "CANoe" / "test.cfg")# CANoe工程cfg绝对路径
 
TEMPLATE_HOMEPAGE01_IMG = str(BASE_DIR / ".." / "testTemplate" / "home_01.png") # HMI局域匹配模板图
TEMPLATE_HOMEPAGE01_KMH_IMG = str(BASE_DIR / ".." / "testTemplate" / "home_01_kmh.png") # HMI局域匹配模板图
TEMPLATE_HOMEPAGE01_BLANK_IMG = str(BASE_DIR / ".." / "testTemplate" / "home_01_blank.png") # HMI局域匹配模板图


TEMPLATE_HOMEPAGE02_IMG = str(BASE_DIR / ".." / "testTemplate" / "home_02.png") # HMI局域匹配模板图
TEMPLATE_HOMEPAGE02_ECO_IMG = str(BASE_DIR / ".." / "testTemplate" / "home_02_eco.png") # HMI局域匹配模板图
TEMPLATE_HOMEPAGE02_POWER_IMG = str(BASE_DIR / ".." / "testTemplate" / "home_02_power.png") # HMI局域匹配模板图
TEMPLATE_HOMEPAGE02_CHARGE_IMG = str(BASE_DIR / ".." / "testTemplate" / "home_02_charge.png") # HMI局域匹配模板图

TEMPLATE_SETTING_IMG = str(BASE_DIR / ".." / "testTemplate" / "setting.png") # HMI局域匹配模板图
TEMPLATE_SETTING_DISPLAY_IMG = str(BASE_DIR / ".." / "testTemplate" / "setting_vehicle_settings.png") # HMI局域匹配模板图

TEMPLATE_VEHICLE_IMG = str(BASE_DIR / ".." / "testTemplate" / "vehicle_service.png") # HMI局域匹配模板图
TEMPLATE_VEHICLE_TYRE_IMG = str(BASE_DIR / ".." / "testTemplate" / "vehicle_tyre_pressure.png") # HMI局域匹配模板图
TEMPLATE_VEHICLE_SERVICEDAY_IMG = str(BASE_DIR / ".." / "testTemplate" / "vehicle_service_serviceday.png") # HMI局域匹配模板图


TEMPLATE_TRIP_IMG = str(BASE_DIR / ".." / "testTemplate" / "trip_a.png") # HMI局域匹配模板图
TEMPLATE_TRIPA_IMG = str(BASE_DIR / ".." / "testTemplate" / "trip_a_consuma.png") # HMI局域匹配模板图
TEMPLATE_TRIPB_IMG = str(BASE_DIR / ".." / "testTemplate" / "trip_b_consumb.png") # HMI局域匹配模板图

TEMPLATE_ACC_SUBMENU_IMG = str(BASE_DIR / ".." / "testTemplate" / "acc_submenu.png") # HMI局域匹配模板图

TEMPLATE_MESSAGE_SUBMENU_IMG = str(BASE_DIR / ".." / "testTemplate" / "message_aeb.png") # HMI局域匹配模板图

TEMPLATE_MUSIC_SUBMENU_IMG = str(BASE_DIR / ".." / "testTemplate" / "music_uconnectoff.png") # HMI局域匹配模板图

TEMPLATE_ODOMETER_IMG = str(BASE_DIR / ".." / "testTemplate" / "home_odometer.png") # HMI局域匹配模板图
TEMPLATE_SPEEDOMETER_IMG = str(BASE_DIR / ".." / "testTemplate" / "speedometer.png") # HMI局域匹配模板图
TEMPLATE_TRIPSUMMARY_IMG = str(BASE_DIR / ".." / "testTemplate" / "tripsummary.png") # HMI局域匹配模板图
TEMPLATE_TRIPSUMMARY_ROI_IMG = str(BASE_DIR / ".." / "testTemplate" / "tripsummaryroi.png") # HMI局域匹配模板图
TEMPLATE_SUMMARY_IMG = str(BASE_DIR / ".." / "testTemplate" / "summary.png") # HMI参考模板图

TEST_IMG = str(BASE_DIR / ".." / "testpic" / "test.png") # HMI参考模板图


CAP_HOME_PAGE_IMG = "cap_home_page.png"  
CAP_SUMMARY_IMG = "cap_summary.png"
CAP_HOME_PAGE_IMG = "cap_home_page.png"

ROI_PAGE_BIG = (0,0,1000,700)
ROI_SUMMARY_PAGE_SUMMARY = ROI_PAGE_BIG
ROI_HOME_PAGE_ODOMETER = (550,620,220,80)
ROI_HOME_PAGE_KMH = (0,0,1000,700)



PAGE_HOME_SUBMENU_TABLE = [
    {"sub_menu_name": "home_01",      "id_pictures":[{"path":TEMPLATE_HOMEPAGE01_KMH_IMG, "roi":ROI_PAGE_BIG, "score":0.9},
                                                     {"path":TEMPLATE_HOMEPAGE01_BLANK_IMG, "roi":ROI_PAGE_BIG, "score":0.9},]},
    {"sub_menu_name": "home_02",      "id_pictures":[{"path":TEMPLATE_HOMEPAGE02_ECO_IMG, "roi":ROI_PAGE_BIG, "score":0.85},
                                                     {"path":TEMPLATE_HOMEPAGE01_KMH_IMG, "roi":ROI_PAGE_BIG, "score":0.9},
                                                     #{"path":TEMPLATE_HOMEPAGE02_POWER_IMG, "roi":(0, 0, 1280, 720), "score":0.9},
                                                     #{"path":TEMPLATE_HOMEPAGE02_CHARGE_IMG, "roi":(0, 0, 1280, 720), "score":0.9},
                                                     ]},
]

PAGE_SETTING_SUBMENU_TABLE = [
    {"sub_menu_name": "setting_01",   "id_pictures":[{"path":TEMPLATE_SETTING_DISPLAY_IMG, "roi":ROI_PAGE_BIG, "score":0.9},
                                                     {"path":TEMPLATE_SETTING_DISPLAY_IMG, "roi":ROI_PAGE_BIG, "score":0.9},]},
]

PAGE_MESSAGE_SUBMENU_TABLE = [
    {"sub_menu_name": "message01",   "id_pictures":[{"path":TEMPLATE_MESSAGE_SUBMENU_IMG, "roi":ROI_PAGE_BIG, "score":0.9},]},
]

PAGE_MUSIC_SUBMENU_TABLE = [
    {"sub_menu_name": "music01",   "id_pictures":[{"path":TEMPLATE_MUSIC_SUBMENU_IMG, "roi":ROI_PAGE_BIG, "score":0.9},]},
]

PAGE_VEHICLE_SUBMENU_TABLE = [
    {"sub_menu_name": "tyre",   "id_pictures":[{"path":TEMPLATE_VEHICLE_TYRE_IMG, "roi":ROI_PAGE_BIG, "score":0.9},]},
    {"sub_menu_name": "serviceday",   "id_pictures":[{"path":TEMPLATE_VEHICLE_SERVICEDAY_IMG, "roi":ROI_PAGE_BIG, "score":0.9},]},
]

PAGE_ACC_SUBMENU_TABLE = [
    {"sub_menu_name": "acc01",   "id_pictures":[{"path":TEMPLATE_ACC_SUBMENU_IMG, "roi":ROI_PAGE_BIG, "score":0.9},]},
]

PAGE_TRIP_SUBMENU_TABLE = [
    {"sub_menu_name": "tripa",   "id_pictures":[{"path":TEMPLATE_TRIPA_IMG, "roi":ROI_PAGE_BIG, "score":0.9},]},
    {"sub_menu_name": "tripb",   "id_pictures":[{"path":TEMPLATE_TRIPB_IMG, "roi":ROI_PAGE_BIG, "score":0.9},]},
]

PAGE_TABLE = [
    {"page_name": "HOME",          "sub_menus":PAGE_HOME_SUBMENU_TABLE},
    {"page_name": "SETTING",       "sub_menus":PAGE_SETTING_SUBMENU_TABLE},
    {"page_name": "MESSAGES",      "sub_menus":PAGE_MESSAGE_SUBMENU_TABLE},
    {"page_name": "MUSIC",         "sub_menus":PAGE_MUSIC_SUBMENU_TABLE},
    {"page_name": "VEHICLE",       "sub_menus":PAGE_VEHICLE_SUBMENU_TABLE},
    {"page_name": "ACC",           "sub_menus":PAGE_ACC_SUBMENU_TABLE},
    {"page_name": "TRIP",          "sub_menus":PAGE_TRIP_SUBMENU_TABLE},
]

