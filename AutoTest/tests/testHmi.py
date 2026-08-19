import pytest
import time
from pathlib import Path
from utils.image_check import template_match_in_roi
BASE_DIR = Path(__file__).resolve().parent
TEMPLATE_NORMAL_IMG = str(BASE_DIR / ".." / "testTemplate" / "normal.png") # HMI参考模板图
TEMPLATE_SUMMARY_IMG = str(BASE_DIR / ".." / "testTemplate" / "summary.png") # HMI参考模板图
ODOMETER_IMG = str(BASE_DIR / ".." / "testTemplate" / "odometer.png") # HMI局域匹配模板图
SPEEDOMETER_IMG = str(BASE_DIR / ".." / "testTemplate" / "speedometer.png") # HMI局域匹配模板图
TRIPSUMMAR_IMG = str(BASE_DIR / ".." / "testTemplate" / "tripsummary.png") # HMI局域匹配模板图

CAP_NORMAL_IMG = "cap_normal.png"
CAP_SUMMARY_IMG = "cap_summary.png"
class TestHMI:
    @pytest.mark.parametrize("loop_index", list(range(3)))
    def test_hmi(self, cam_recorder, cam_picture, canoe_api, kl15, case_logger, case_logger_dir, loop_index):
        print(f"Round {loop_index+1} Excuting...")
        canoeApi = canoe_api
        assert (canoeApi != None)
        
        #KL15 on
        kl15.kl15on()
        print("KL15 ON")
        time.sleep(20)
        
        print("Folder exist：", Path(case_logger_dir).exists())
        #set the CAN log directory
        blf_file_path = str(Path(case_logger_dir) / "bus_log.asc")
        canoe_api.set_logging_blf_path(blf_file_path, logger_index=1)
        
        measurement = canoe_api.app.Measurement
 
        # 启动测量
        if not measurement.Running:
            measurement.Start()
        print("Start the CANOE measurement.")
        time.sleep(20) # 等待HMI界面刷新
        #capture the HMI picture
        cam_picture.camera_capture_one(1280, 720, case_logger_dir, CAP_NORMAL_IMG)
        roi = (400, 500, 400, 100)
        big_img_path = str(Path(case_logger_dir) / CAP_NORMAL_IMG)
        
        #check odometer match
        exists, score, pos = template_match_in_roi(big_img_path, ODOMETER_IMG, roi, threshold=0.8)
        print(f"Match odometer points: {score:.3f}")
        assert exists is True
        
        roi = (400, 250, 300, 200)
        exists, score, pos = template_match_in_roi(big_img_path, SPEEDOMETER_IMG, roi, threshold=0.8)
        print(f"Match speedometer points: {score:.3f}")
        if exists:
            print("pos: ", {pos})
        assert exists is True
        #check speedometer match
        
        time.sleep(20)
        #check energy match
        
        #capture the summary page
        #check summary page
        cam_picture.camera_capture_one(1280, 720, case_logger_dir, CAP_SUMMARY_IMG)
        roi = (200, 150, 700, 450)
        big_img_path = str(Path(case_logger_dir) / CAP_SUMMARY_IMG)
        exists, score, pos = template_match_in_roi(big_img_path, TRIPSUMMAR_IMG, roi, threshold=0.8)
        print(f"Match trip summary points: {score:.3f}")
        assert exists is True
        
        time.sleep(10)
        # 2. OpenCV摄像头视觉比对
        #ssim_score = cam_picture.calc_ssim_camera_vs_template(TEMPLATE_IMG, case_logger_dir)
        #print(f"SSIM相似度 = {ssim_score}")
        time.sleep(20)  # 等待CAN message end
        
        #shut down KL15, stop the measurement
        kl15.kl15off()
        if measurement.Running:
            measurement.Stop()
        time.sleep(10) 
     
        # 4. pytest断言：相似度大于0.92才算PASS
        #assert ssim_score >= 0.92, f"HMI界面校验失败，SSIM={ssim_score}" 
        pass
        
     