import pytest
import time
from pathlib import Path
from utils.image_check import template_match_in_roi
from utils.hmi_control import finding_home_page, get_current_page, go_to_page, show_all_pages
from tests.config import PAGE_TABLE

import logging
logger = logging.getLogger(__name__)

class TestHMI:
    @pytest.mark.skipif(True, reason="CANoe环境未就绪，临时关闭")
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
    @pytest.mark.skipif(True, reason="CANoe环境未就绪，临时关闭")
    @pytest.mark.parametrize("loop_index", list(range(1)))    
    def test_send_can_and_check_signal(self, cam_recorder, cam_picture, canoe_api, kl15, case_logger, case_logger_dir, loop_index):
        print(f"Round {loop_index+1} Excuting...")
        canoeApi = canoe_api
        assert (canoeApi != None)
        
        #KL15 on
        kl15.kl15on()
        print("KL15 ON")
        
        # button OK 11 data=[0x00, 0x10, 0x00, 0x00]
        # button UP 12 data=[0x00, 0x40, 0x00, 0x00]
        # button DOWN 13  data=[0x01, 0x00, 0x00, 0x00]
        # button RIGHT 14 data=[0x04, 0x00, 0x00, 0x00]
        # button LEFT  15 data=[0x10, 0x10, 0x00, 0x00]
        
        print("Folder exist：", Path(case_logger_dir).exists())
        #set the CAN log directory
        blf_file_path = str(Path(case_logger_dir) / "bus_log.asc")
        canoe_api.set_logging_blf_path(blf_file_path, logger_index=1)
        
        measurement = canoe_api.app.Measurement
 
        # 启动测量
        if not measurement.Running:
            measurement.Start()
        print("Start the CANOE measurement.")
        time.sleep(10)  # 等待总线响应
        
        keyonState = canoeApi.get_sys_var("Sysv_IGWorkCondition", "Sysv_IGWorkCondition")
        
        print("\n Sysv_IGWorkCondition ", keyonState)
        
        
        canoeApi.set_sys_var("Sysv_IGWorkCondition", "Sysv_IGWorkCondition", 5)
        time.sleep(1) 
        print("\n Sysv_IGWorkCondition ", canoeApi.get_sys_var("Sysv_IGWorkCondition", "Sysv_IGWorkCondition"))
        # 1. 发送CAN ID=0x123，8字节数据
        #canoe_api.canoe_send_can_message(
        #    channel=1,
        #    msg_id=0x2EE,
        #    data=[0x04, 0x00, 0x00, 0x00]
        #)
        time.sleep(30)  # 等待总线响应
        finding_home_page(canoe_api, cam_picture, case_logger_dir, 50.0, 0.5)
        
        # 1. 发送CAN ID=0x123，8字节数据
        #canoe_api.canoe_send_can_message(
        #    channel=1,
        #    msg_id=0x2EE,
        #    data=[0x04, 0x00, 0x00, 0x00]
        #)
        time.sleep(2)  # 等待总线响应
        
        # 1. 发送CAN ID=0x123，8字节数据
        #canoe_api.canoe_send_can_message(
        #    channel=1,
        #    msg_id=0x2EE,
        #    data=[0x04, 0x00, 0x00, 0x00]

        time.sleep(2)  # 等待总线响应

        # 2. 读取反馈信号
        #speed_val = canoe_get_signal_value("CAN::EngineMsg::EngineSpeed")
        #print(f"读取发动机转速 = {speed_val}")

        # 断言
        #assert speed_val > 800 
        pass
    @pytest.mark.skipif(True, reason="CANoe环境未就绪，临时关闭")    
    @pytest.mark.parametrize("loop_index", list(range(1)))    
    def test_find_page(self, case_logger, case_logger_dir, loop_index):
        print(f"Round {loop_index+1} Excuting...")
        
        valid, page_name, sub_menu_name = get_current_page(TEMPLATE_NORMAL_IMG)
        print("valid, page_name, sub_menu_name: ", valid, page_name, sub_menu_name)

        time.sleep(2)  # 等待总线响应

        pass
    @pytest.mark.skipif(True, reason="CANoe环境未就绪，临时关闭")        
    @pytest.mark.parametrize("loop_index", list(range(1)))    
    def test_goto_page(self, cam_recorder, cam_picture, canoe_api, kl15, case_logger, case_logger_dir, loop_index):
        print(f"Round {loop_index+1} Excuting...")
        canoeApi = canoe_api
        assert (canoeApi != None)
        
        #KL15 on
        kl15.kl15on()
        print("KL15 ON")
        
        
        print("Folder exist：", Path(case_logger_dir).exists())
        #set the CAN log directory
        blf_file_path = str(Path(case_logger_dir) / "bus_log.asc")
        canoe_api.set_logging_blf_path(blf_file_path, logger_index=1)
        
        measurement = canoe_api.app.Measurement
 
        # 启动测量
        if not measurement.Running:
            measurement.Start()
        print("Start the CANOE measurement.")
        time.sleep(20)  # 等待总线响应
        
        keyonState = canoeApi.get_sys_var("Sysv_IGWorkCondition", "Sysv_IGWorkCondition")
        
        print("\n Sysv_IGWorkCondition ", keyonState)
        
        
        canoeApi.set_sys_var("Sysv_IGWorkCondition", "Sysv_IGWorkCondition", 5)
        time.sleep(1) 
        print("\n Sysv_IGWorkCondition ", canoeApi.get_sys_var("Sysv_IGWorkCondition", "Sysv_IGWorkCondition"))
        ret = go_to_page("HOME", "home_01", canoe_api, cam_picture, case_logger_dir, 60, 2)
        
        print("\n go to page RET: ", ret)

        time.sleep(2)  # 等待总线响应
        #shut down KL15, stop the measurement
        kl15.kl15off()
        if measurement.Running:
            measurement.Stop()
        time.sleep(10) 
        pass    
    @pytest.mark.parametrize("loop_index", list(range(1)))    
    def test_show_page(self, cam_recorder, cam_picture, canoe_api, kl15, case_logger, case_logger_dir, loop_index):
        print(f"Round {loop_index+1} Excuting...")
        
        logger.info(f"Start using logger loop_index = {loop_index} .")
        
        canoeApi = canoe_api
        assert (canoeApi != None)
        
        #KL15 on
        kl15.kl15on()
        print("KL15 ON")
        
        
        print("Folder exist：", Path(case_logger_dir).exists())
        #set the CAN log directory
        blf_file_path = str(Path(case_logger_dir) / "bus_log.asc")
        canoe_api.set_logging_blf_path(blf_file_path, logger_index=1)
        
        measurement = canoe_api.app.Measurement
 
        # 启动测量
        if not measurement.Running:
            measurement.Start()
        print("Start the CANOE measurement.")
        time.sleep(20)  # 等待总线响应
        
        keyonState = canoeApi.get_sys_var("Sysv_IGWorkCondition", "Sysv_IGWorkCondition")
        
        print("\n Sysv_IGWorkCondition ", keyonState)
        
        
        canoeApi.set_sys_var("Sysv_IGWorkCondition", "Sysv_IGWorkCondition", 5)
        time.sleep(1) 
        print("\n Sysv_IGWorkCondition ", canoeApi.get_sys_var("Sysv_IGWorkCondition", "Sysv_IGWorkCondition"))
        ret = show_all_pages(canoe_api, cam_picture, case_logger_dir, 120, 3)

        time.sleep(2)  # 等待总线响应
        #shut down KL15, stop the measurement
        kl15.kl15off()
        if measurement.Running:
            measurement.Stop()
        time.sleep(10) 
        pass        

