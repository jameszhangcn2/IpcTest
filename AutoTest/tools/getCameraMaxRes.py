import cv2

COMMON_RES = [
    (3840, 2160),
    (2560, 1440),
    (1920, 1080),
    (1280, 720),
    (1024, 768),
    (800, 600),
    (640, 480),
    (320, 240)
]


def get_camera_max_res_fast(cam_id=0):
    cap = cv2.VideoCapture(cam_id, cv2.CAP_DSHOW)
    if not cap.isOpened():
        raise RuntimeError("相机打开失败")
    max_res = None
    for w_test, h_test in COMMON_RES:
        cap.set(cv2.CAP_PROP_FRAME_WIDTH, w_test)
        cap.set(cv2.CAP_PROP_FRAME_HEIGHT, h_test)
        cap.set(cv2.CAP_PROP_FOURCC, cv2.VideoWriter_fourcc(*"MJPG"))
        ret, frame = cap.read()
        if ret:
            h_real, w_real = frame.shape[:2]
            max_res = (w_real, h_real)
            break
    cap.release()
    return max_res
	
	# ======================调用示例======================
if __name__ == "__main__":
    res = get_camera_max_res_fast(cam_id=1)
    if res is not None:
        cam_w, cam_h = res
        print(f"相机最大分辨率 width={cam_w}, height={cam_h}")
    else:
        print("未获取到相机分辨率")