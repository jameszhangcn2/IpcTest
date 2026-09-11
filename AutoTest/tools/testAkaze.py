import cv2
import numpy as np
from pathlib import Path
import os
from utils.image_check import template_match_in_roi, match_hmi_by_edge_roi, match_hmi_orb, is_template_matched, nms_detections, akaze_template_detect_roi, draw_roi_box, draw_detection_box
from tests.config import ROI_PAGE_BIG, DEBUG_SAVE_EDGE, DEBUG_SAVE_DIR
import logging
from utils.camera_picture import CameraPicture
from utils.hmi_control import finding_home_page, get_current_page, go_to_page, show_all_pages

BASE_DIR = Path(__file__).resolve().parent

TEST_DIR = str(BASE_DIR / ".." / "tools/testpic") # HMI局域匹配模板图
BIG_IMG = str(BASE_DIR / ".." / "tools/testpic" / "TripA_uniform.png") # HMI局域匹配模板图
TEMPLATE_IMG = str(BASE_DIR / ".." / "tools/testpic" / "home_odometer3.png") # HMI局域匹配模板图

logger = logging.getLogger(__name__)

class TestAkaze:
    def test_akaze(self, request, cam_picture, serial_mcu_bg_monitor):


        tempPic = BIG_IMG
        tempUniformPic = "TripA_uniform.png"
        #ret = cam_picture.camera_uniform_pic(tempPic, TEST_DIR, tempUniformPic)

        scene_path = BIG_IMG
        #template_list = [TEMPLATE_IMG, TEMPLATE_IMG]
        template_list = [TEMPLATE_IMG]
        roi_area = (550, 600, 200, 50)
        # roi_area = None

        #akaze = cv2.AKAZE_create(threshold=0.0015, nOctaves=4, nOctaveLayers=4)
        scene_bgr = cv2.imread(scene_path)

        gray = cv2.cvtColor(scene_bgr, cv2.COLOR_BGR2GRAY)

        # CLAHE对比度增强
        clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8,8))
        gray_enhance = clahe.apply(gray)

        # AKAZE正确创建方式
        akaze = cv2.AKAZE.create()
        kp, des = akaze.detectAndCompute(gray_enhance, None)

        if scene_bgr is None:
            print("场景图片读取失败")
        else:
            raw_results: List[Dict] = []
            for tpl_file in template_list:
                res = akaze_template_detect_roi(
                    tpl_file,
                    scene_bgr,
                    akaze,
                    roi=roi_area,
                    use_clahe=True,      #开启CLAHE，反光场景建议True
                    clip_limit=2.2,
                    grid=(8,8),
                    lowe_ratio=0.72,
                    min_inliers=5,
                    ransac_thresh=5.0
                )
                if res is not None:
                    raw_results.append(res)
            final_results = nms_detections(raw_results, iou_thr=0.45)
            print(f"原始检出数量:{len(raw_results)},NMS保留数量:{len(final_results)}")
            for r in final_results:
                print(f"【{r['template']}】中心点{r['center']},角度={r['angle_deg']:.2f},内点={r['inliers']}")

            canvas = scene_bgr.copy()
            canvas = draw_roi_box(canvas, roi_area)
            colors = [(0, 255, 0), (255, 0, 0), (0, 255, 255)]
            for idx, r in enumerate(final_results):
                canvas = draw_detection_box(canvas, r, colors[idx % len(colors)])

            cv2.imshow("AKAZE+ROI+NMS+CLAHE", canvas)

            # 绘制特征点
            out_img = cv2.drawKeypoints(gray_enhance, kp, None)
            cv2.imshow("akaze", out_img)

            cv2.waitKey(0)
            cv2.destroyAllWindows()