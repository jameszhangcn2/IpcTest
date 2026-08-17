import cv2
import datetime

class CameraRecorder:
    def __init__(self, save_root: Path, fps: int = 30, camera_id: int = 0):
        self.save_root = save_root
        self.fps = fps
        self.camera_id = camera_id
        self.cap: Optional[cv2.VideoCapture] = None
        self.writer: Optional[cv2.VideoWriter] = None
        self.video_path: str = ""

    def start_record(self, case_name: str):
        """启动摄像头+录像"""
        # 打开摄像头
        self.cap = cv2.VideoCapture(self.camera_id)
        if not self.cap.isOpened():
            raise RuntimeError(f"无法打开摄像头 id={self.camera_id}")

        # 获取摄像头分辨率
        width = int(self.cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        height = int(self.cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        print(f"[Camera width] {width}")
        print(f"[Camera height] {height}")

        # 路径构造
        time_str = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        date_folder = self.save_root / datetime.datetime.now().strftime("%Y%m%d")
        date_folder.mkdir(parents=True, exist_ok=True)
        self.video_path = str(date_folder / f"{time_str}_{case_name}.mp4")

        fourcc = cv2.VideoWriter_fourcc(*"mp4v")
        self.writer = cv2.VideoWriter(self.video_path, fourcc, self.fps, (width, height))
        print(f"[Camera Record START] {self.video_path}")

    def grab_frame(self):
        """读取一帧写入视频（子线程循环调用）"""
        if self.cap is None or self.writer is None:
            return
        ret, frame = self.cap.read()
        if ret:
            self.writer.write(frame)

    def stop_record(self):
        """释放摄像头、保存文件"""
        if self.writer:
            self.writer.release()
        if self.cap:
            self.cap.release()
        print(f"[Camera Record SAVED] {self.video_path}")
        self.writer = None
        self.cap = None
        