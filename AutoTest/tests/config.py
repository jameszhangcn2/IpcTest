from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
CAP_HOME_PAGE_IMG = "cap_home_page.png"   
ODOMETER_IMG = str(BASE_DIR / ".." / "testTemplate" / "odometer.png") # HMI局域匹配模板图
SPEEDOMETER_IMG = str(BASE_DIR / ".." / "testTemplate" / "speedometer.png") # HMI局域匹配模板图
TRIPSUMMAR_IMG = str(BASE_DIR / ".." / "testTemplate" / "tripsummary.png") # HMI局域匹配模板图


PAGE_HOME_SUBMENU_TABLE = [
    {"sub_menu_name": "home_01",      "id_pictures":[{"path":SPEEDOMETER_IMG, "roi":(620, 256, 140, 171), "score":0.6},]},
    {"sub_menu_name": "home_02",      "id_pictures":[{"path":ODOMETER_IMG, "roi":(400, 250, 300, 200), "score":0.6},
                                                     {"path":SPEEDOMETER_IMG, "roi":(400, 250, 300, 200), "score":0.7},]},
]

PAGE_SETTING_SUBMENU_TABLE = [
    {"sub_menu_name": "setting_01",   "id_pictures":[{"path":TRIPSUMMAR_IMG, "roi":(200, 150, 700, 450), "score":0.6},
                                                     {"path":TRIPSUMMAR_IMG, "roi":(200, 150, 700, 450), "score":0.6},]},
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

