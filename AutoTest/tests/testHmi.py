import pytest
import time
from pathlib import Path
from utils.image_check import template_match_in_roi
from utils.hmi_control import finding_home_page, get_current_page, go_to_page, show_all_pages
from utils.camera_picture import is_summary_page_match, is_odometer_page_match
from tests.config import PAGE_TABLE, TEST_IMG

import logging

logger = logging.getLogger(__name__)

class TestHMI:
    #@pytest.mark.skipif(True, reason="Not ready, temporary close.")
    @pytest.mark.parametrize("loop_index", list(range(20)))
    def test_hmi(self, request, cam_recorder, cam_picture, canoe_api, kl15, case_logger, case_logger_dir, loop_index):
        case_name = request.node.nodeid.replace("/", "_").replace("\\", "_").replace(":", "_")
        logger.info(f"Round {loop_index+1} Excuting... {case_name}")
        canoeApi = canoe_api
        assert (canoeApi != None)
        
        logger.info("Folder exist: %d %s", Path(case_logger_dir).exists(), case_logger_dir)
        #set the CAN log directory
        blf_file_path = str(Path(case_logger_dir) / "bus_log.asc")
        canoe_api.set_logging_blf_path(blf_file_path, logger_index=1)
        
        measurement = canoe_api.app.Measurement
 
        # 启动测量
        if not measurement.Running:
            measurement.Start()
        logger.info("Start the CANOE measurement.")
        time.sleep(10) # wait start up
        #KL15 on
        kl15.kl15on()
        logger.info("KL15 ON")

        canoeApi.set_sys_var("Sysv_IGWorkCondition", "Sysv_IGWorkCondition", 5)
        logger.info("Send Key On.") 
        time.sleep(1)
        logger.info("sv_IGWorkCondition %d", canoeApi.get_sys_var("Sysv_IGWorkCondition", "Sysv_IGWorkCondition"))

        time.sleep(30)

        #check if page at HOME submenu 02
        tempPic = "capture_home_02_page.png"
        tempUniformPic = "capture_home_02_page_uniformd.png"
        cam_picture.camera_capture_one(case_logger_dir, tempPic)
        ret = cam_picture.camera_uniform_pic(tempPic, case_logger_dir, tempUniformPic)
        valid = False
        current_page_name = None
        current_sub_menu_name = None
        big_img_path = None
        if ret:
            big_img_path = str(Path(case_logger_dir) / tempUniformPic)
            valid, current_page_name, current_sub_menu_name = get_current_page(big_img_path)
        logger.info("valid %d, current_page_name %s, current_sub_menu_name %s big_img_path %s", 
                    valid, current_page_name, current_sub_menu_name, big_img_path)

        ind_page_match = (current_page_name == "HOME") and (current_sub_menu_name == "home_02")
        if ind_page_match == False:
            ret = go_to_page("HOME", "home_02", canoe_api, cam_picture, case_logger_dir, 120, 0.2)
            logger.info("go to page RET %d", ret)
        
        #check odometer
        odometer_match = False
        if big_img_path != None:
            odometer_match, val = is_odometer_page_match(big_img_path)
            logger.info("odometer_match %d val %f", odometer_match, val)
        assert(odometer_match)

        #check summary
        canoeApi.set_sys_var("Sysv_IGWorkCondition", "Sysv_IGWorkCondition", 1)
        logger.info("Send Key Off.") 
        time.sleep(2)
        logger.info("sv_IGWorkCondition %d", canoeApi.get_sys_var("Sysv_IGWorkCondition", "Sysv_IGWorkCondition"))

        tempPic = "capture_summary_page.png"
        tempUniformPic = "capture_summary_page_uniformd.png"
        cam_picture.camera_capture_one(case_logger_dir, tempPic)
        ret = cam_picture.camera_uniform_pic(tempPic, case_logger_dir, tempUniformPic)

        summary_match = False
        if ret:
            big_img_path = str(Path(case_logger_dir) / tempUniformPic)
            summary_match, val = is_summary_page_match(big_img_path)
            logger.info("summary_match %d val %f", summary_match, val)
        else:
            logger.info("Can not get the summary page.")
            assert(ret)
        assert(summary_match)
        
        if measurement.Running:
            measurement.Stop()
        #shut down KL15, stop the measurement
        kl15.kl15off()
        time.sleep(5) 
        assert(ind_page_match)

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
    @pytest.mark.skipif(True, reason="Not ready, temporary close.")    
    @pytest.mark.parametrize("loop_index", list(range(1)))    
    def test_find_page(self, case_logger, case_logger_dir, loop_index):
        logger.info(f"Round {loop_index+1} Excuting...")
        
        valid, page_name, sub_menu_name = get_current_page(TEST_IMG)
        logger.info("valid %d page_name %s sub_menu_name %s", valid, page_name, sub_menu_name)

        time.sleep(2)  # 等待总线响应

        pass
    @pytest.mark.skipif(True, reason="Not ready, temporary close.")    
    @pytest.mark.parametrize("loop_index", list(range(1)))    
    def test_goto_page(self, cam_recorder, cam_picture, canoe_api, kl15, case_logger, case_logger_dir, loop_index):
        logger.info(f"Round {loop_index+1} Excuting...")
        canoeApi = canoe_api
        assert (canoeApi != None)
        
        #KL15 on
        kl15.kl15on()
        logger.info("KL15 ON")
        
        
        logger.info("Folder exist %d", Path(case_logger_dir).exists())
        #set the CAN log directory
        blf_file_path = str(Path(case_logger_dir) / "bus_log.asc")
        canoe_api.set_logging_blf_path(blf_file_path, logger_index=1)
        
        measurement = canoe_api.app.Measurement
 
        # start measurement
        if not measurement.Running:
            measurement.Start()
        logger.info("Start the CANOE measurement.")
        time.sleep(20) 
        
        canoeApi.set_sys_var("Sysv_IGWorkCondition", "Sysv_IGWorkCondition", 5)
        logger.info("Send Key On.")
        time.sleep(5) 
        logger.info("sv_IGWorkCondition %d", canoeApi.get_sys_var("Sysv_IGWorkCondition", "Sysv_IGWorkCondition"))
        #ret = go_to_page("SETTING", "setting_01", canoe_api, cam_picture, case_logger_dir, 60, 2)
        ret = go_to_page("HOME", "home_02", canoe_api, cam_picture, case_logger_dir, 300, 0.2)
        
        logger.info("go to page RET %d", ret)

        time.sleep(2) 
        #shut down KL15, stop the measurement
        kl15.kl15off()
        logger.info("KL15 off.")
        if measurement.Running:
            measurement.Stop()
            logger.info("Stop the CANOE measurement.")
        time.sleep(10) 
        pass
    @pytest.mark.skipif(True, reason="Not ready, temparary suspend.")                
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
        canoeApi.set_sys_var("Sysv_IGWorkCondition", "Sysv_IGWorkCondition", 1)
        time.sleep(1) 
        time.sleep(2)  # 等待总线响应
        #shut down KL15, stop the measurement
        kl15.kl15off()
        if measurement.Running:
            measurement.Stop()
        time.sleep(10) 
        pass        

