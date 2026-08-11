import time
from pathlib import Path
BASE_DIR = Path(__file__).resolve().parent
TEMPLATE_IMG = str(BASE_DIR / ".." / "CANoe" / "demo.png") # HMI参考模板图
class TestHMI:
    def test_hmi(self, cam_recorder, cam_picture, canoe_api):
        canoeApi = canoe_api
        assert (canoeApi != None)
        
        keyonState = canoeApi.get_sys_var("Sysv_IGWorkCondition", "Sysv_IGWorkCondition")
        
        print("\n Sysv_IGWorkCondition ", keyonState)
        
        
        canoeApi.set_sys_var("Sysv_IGWorkCondition", "Sysv_IGWorkCondition", 5)
        time.sleep(1) 
        print("\n Sysv_IGWorkCondition ", canoeApi.get_sys_var("Sysv_IGWorkCondition", "Sysv_IGWorkCondition"))
     
        # 1. 设置总线信号 VehicleSpeed=80
        # set_signal(canoe, "VehicleSpeed", "DemoDB", 80)
        time.sleep(20)  # 等待HMI界面刷新
        # 2. OpenCV摄像头视觉比对
        ssim_score = cam_picture.calc_ssim_camera_vs_template(TEMPLATE_IMG)
        print(f"SSIM相似度 = {ssim_score}")
     
        # 3. 将视觉结果回写给CANoe系统变量
        #set_sys_var(canoe, "VisualTest", "SSIM_Result", ssim_score)
        
        # keyoff
        canoeApi.set_sys_var("Sysv_IGWorkCondition", "Sysv_IGWorkCondition", 1)
        time.sleep(1) 
     
        # 4. pytest断言：相似度大于0.92才算PASS
        assert ssim_score >= 0.92, f"HMI界面校验失败，SSIM={ssim_score}"
        pass
