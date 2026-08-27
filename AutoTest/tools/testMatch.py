import cv2
import numpy as np
from pathlib import Path
import os
from utils.image_check import template_match_in_roi, match_hmi_by_edge_roi, match_hmi_orb, is_template_matched
from tests.config import ROI_PAGE_BIG, DEBUG_SAVE_EDGE, DEBUG_SAVE_DIR
import logging

BASE_DIR = Path(__file__).resolve().parent

BIG_IMG = str(BASE_DIR / ".." / "tools/testpic" / "capture_home_02_page_uniformd.png") # HMI局域匹配模板图
TEMPLATE_IMG = str(BASE_DIR / ".." / "tools/testpic" / "home_odometer3.png") # HMI局域匹配模板图

logger = logging.getLogger(__name__)

class TestMatch:
    def test_match(self, request):
        
        hmi_img = cv2.imread(BIG_IMG)
        tpl = cv2.imread(TEMPLATE_IMG)
        found, max_val, match_pos = template_match_in_roi(BIG_IMG, TEMPLATE_IMG, ROI_PAGE_BIG)
        logger.info(f"match 区域匹配得分:{max_val:.3f}, result={found}")

        #与ROI不同，这里是左上，右下
        #(cx, cy, rw, rh) = ROI_PAGE_BIG
        (cx, cy, rw, rh) = (550,550,700,600)
        x1 = cx
        y1 = cy
        x2 = cx + rw
        y2 = cy + rh
        roi_area = (x1,y1,x2,y2)
        is_match, score, pos, w, h = match_hmi_by_edge_roi(
            hmi_warped_frame=hmi_img,
            template_img=tpl,
            roi=roi_area,
            thresh=0.7
        )

        logger.info(f"ROI区域匹配得分:{score:.3f}, result={is_match}")
        if is_match:
            # 可选：在完整HMI图上画框验证
            x1, y1 = pos
            x2 = x1 + w
            y2 = y1 + h
            cv2.rectangle(hmi_img, (x1, y1), (x2, y2), (0,255,0), 2)
            cv2.imwrite("debug_blue_text_match.jpg", hmi_img)


        is_match, cnt, good, kp1, kp2 = match_hmi_orb(hmi_img, tpl)
        dbg_img = cv2.drawMatches(hmi_img, kp1, tpl, kp2, good, None, flags=cv2.DrawMatchesFlags_NOT_DRAW_SINGLE_POINTS)
        cv2.imwrite("debug_orb_match.jpg", dbg_img)
        logger.info(f"ORB匹配 有效点数:{cnt}, match={is_match}")


        found, max_val, match_method = is_template_matched(BIG_IMG, TEMPLATE_IMG, ROI_PAGE_BIG)
        logger.info(f"is_template_matched:{max_val}, match={found} match_method:{match_method}")
        #cv2.imshow("debug", hmi_img)
        #cv2.waitKey(0)
        #cv2.destroyAllWindows()