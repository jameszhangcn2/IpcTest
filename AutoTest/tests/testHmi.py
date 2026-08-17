import pytest
import time
from pathlib import Path
BASE_DIR = Path(__file__).resolve().parent
TEMPLATE_IMG = str(BASE_DIR / ".." / "testTemplate" / "normal.png") # HMI参考模板图
class TestHMI:
    @pytest.mark.parametrize("loop_index", list(range(10)))
    def test_hmi(self, cam_recorder, cam_picture, canoe_api, kl15, loop_index):
        print(f"第 {loop_index+1} 轮执行")
        canoeApi = canoe_api
        assert (canoeApi != None)
        kl15.kl15on()
        
        measurement = canoe_api.app.Measurement
 
        # 启动测量
        if not measurement.Running:
            measurement.Start()
        time.sleep(30) # 等待HMI界面刷新
        
        # 2. OpenCV摄像头视觉比对
        ssim_score = cam_picture.calc_ssim_camera_vs_template(TEMPLATE_IMG)
        print(f"SSIM相似度 = {ssim_score}")
        time.sleep(40)  # 等待CAN message end
        
        #shut down KL15, stop the measurement
        kl15.kl15off()
        if measurement.Running:
            measurement.Stop()
        time.sleep(20) 
     
        # 4. pytest断言：相似度大于0.92才算PASS
        assert ssim_score >= 0.92, f"HMI界面校验失败，SSIM={ssim_score}" 
        pass