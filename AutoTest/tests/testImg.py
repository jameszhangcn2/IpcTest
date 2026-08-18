import pytest
import time
from utils.image_check import template_match_exist
from pathlib import Path
BASE_DIR = Path(__file__).resolve().parent
TEMPLATE_IMG = str(BASE_DIR / ".." / "testTemplate" / "normal.png") # HMI参考模板图
#ODOMETER_IMG = str(BASE_DIR / ".." / "testTemplate" / "odometerFake.png") # HMI局域匹配模板图
ODOMETER_IMG = str(BASE_DIR / ".." / "testTemplate" / "odometer.png") # HMI局域匹配模板图
class TestIMG:
    @pytest.mark.parametrize("loop_index", list(range(5))) 
    def test_check_icon_exists(self, case_logger_dir, case_logger, loop_index, cam_recorder, cam_picture):
        print(f"第 {loop_index+1} 轮执行")
        # 截图文件（执行测试前先完成截图动作）
        screen_img = TEMPLATE_IMG
        target_icon = ODOMETER_IMG

        exists, score, pos = template_match_exist(screen_img, target_icon, threshold=0.8)
        print(f"最大匹配分数: {score:.3f}")
        
        ssim_score = cam_picture.calc_ssim_camera_vs_template(TEMPLATE_IMG, case_logger_dir)
        print(f"SSIM相似度 = {ssim_score}")
        
        time.sleep(10)
        # pytest断言：界面元素必须存在
        assert exists is True, f"未找到目标图标，匹配分数仅 {score:.3f}"
        
        
        