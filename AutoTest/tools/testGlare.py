import cv2
import numpy as np
from pathlib import Path
import os
from utils.camera_picture import remove_hmi_glare
from tests.config import ROI_PAGE_BIG, DEBUG_SAVE_EDGE, DEBUG_SAVE_DIR
import logging

BASE_DIR = Path(__file__).resolve().parent

BIG_IMG = str(BASE_DIR / ".." / "tools/testpic" / "page_11_1_uniformd.png") # HMI局域匹配模板图
OUTPUT_IMG = str(BASE_DIR / ".." / "tools/testpic" / "debug_afterRemoveglare.png") # HMI局域匹配模板图

logger = logging.getLogger(__name__)

class TestGlare:
    def test_glare(self, request):
        hmi_img = cv2.imread(BIG_IMG)
        output = remove_hmi_glare(hmi_img)
        cv2.imwrite(OUTPUT_IMG, output)