import pytest
import time
from utils.image_check import template_match_exist
from utils.image_check import template_match_in_roi
from pathlib import Path
import logging
logger = logging.getLogger(__name__)

from tests.config import TEMPLATE_HOMEPAGE_IMG, TEMPLATE_SPEEDOMETER_IMG


class TestIMG:
    @pytest.mark.parametrize("loop_index", list(range(1))) 
    def test_check_icon_exists(self, case_logger_dir, case_logger, loop_index, cam_recorder, cam_picture):
        print(f"第 {loop_index+1} 轮执行")
        logger.info("Logger loop: %d.", loop_index)
        # 截图文件（执行测试前先完成截图动作）
        screen_img = TEMPLATE_HOMEPAGE_IMG
        target_icon = TEMPLATE_SPEEDOMETER_IMG

        exists, score, pos = template_match_exist(screen_img, target_icon, threshold=0.8)
        print(f"最大匹配分数: {score:.3f}")
        
        roi = (400, 500, 150, 200)
        exists, score, pos = template_match_in_roi(screen_img, target_icon, roi, threshold=0.8)
        print(f"最大匹配分数: {score:.3f}")
        time.sleep(10)
        # pytest断言：界面元素必须存在
        assert exists is True, f"未找到目标图标，匹配分数仅 {score:.3f}"
        
        
        