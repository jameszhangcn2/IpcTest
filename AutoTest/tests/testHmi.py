import pytest
import time
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
TEMPLATE_IMG = str(BASE_DIR / ".." / "testTemplate" / "normal.png") # HMI参考模板图
class TestHMI:
    @pytest.mark.parametrize("loop_index", list(range(1)))
    def test_hmi(self, cam_recorder, cam_picture, canoe_api, kl15, case_logger, case_logger_dir, loop_index):
        print(f"第 {loop_index+1} 轮执行")
        canoeApi = canoe_api
        assert (canoeApi != None)
        
        kl15.kl15on()
        time.sleep(20)
        
        print("文件夹是否存在：", Path(case_logger_dir).exists())
        # 2. CANoe BLF路径，同一文件夹
        blf_file_path = str(Path(case_logger_dir) / "bus_log.asc")
        #print("文件是否存在：", blf_file_path.exists())
        
        # 设置CANoe日志输出到当前用例目录
        canoe_api.set_logging_blf_path(blf_file_path, logger_index=1)
        
        measurement = canoe_api.app.Measurement
 
        # 启动测量
        if not measurement.Running:
            measurement.Start()
        time.sleep(20) # 等待HMI界面刷新
        
        # 2. OpenCV摄像头视觉比对
        ssim_score = cam_picture.calc_ssim_camera_vs_template(TEMPLATE_IMG, case_logger_dir)
        print(f"SSIM相似度 = {ssim_score}")
        time.sleep(45)  # 等待CAN message end
        
        #shut down KL15, stop the measurement
        kl15.kl15off()
        if measurement.Running:
            measurement.Stop()
        time.sleep(10) 
     
        # 4. pytest断言：相似度大于0.92才算PASS
        assert ssim_score >= 0.92, f"HMI界面校验失败，SSIM={ssim_score}" 
        pass
        
     