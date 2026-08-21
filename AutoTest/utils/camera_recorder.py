import cv2
import datetime
from pathlib import Path
class CameraRecorder:
    def __init__(self, fps: int = 30, camera_id: int = 0):
        self.fps = fps
        self.camera_id = camera_id
        self.cap: Optional[cv2.VideoCapture] = None
        self.writer: Optional[cv2.VideoWriter] = None
        self.video_path: str = ""

    def start_record(self, case_name: str, log_dir: str):
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
        
        # 设置分辨率（可选）
        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)
        
        width = int(self.cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        height = int(self.cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        print(f"[Camera width] {width}")
        print(f"[Camera height] {height}")


        # 路径构造
        time_str = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        #date_folder = self.save_root / datetime.datetime.now().strftime("%Y%m%d")
        #date_folder.mkdir(parents=True, exist_ok=True)
        date_folder = Path(log_dir)
        print("文件夹是否存在：", date_folder.exists())
        self.video_path = str(date_folder / "video.mp4")

        fourcc = cv2.VideoWriter_fourcc(*"mp4v")
        self.writer = cv2.VideoWriter(self.video_path, fourcc, self.fps, (width, height))
        print(f"[Camera Record START] {self.video_path}")
        if not self.writer.isOpened():
            raise RuntimeError(f"VideoWriter 初始化失败！路径={self.video_path}, 分辨率(width={width},height={height})")

    def grab_frame(self):
        """读取一帧写入视频（子线程循环调用）"""
        if self.cap is None or self.writer is None:
            print(f"[grab_frame] failed!!!")
            return
        ret, frame = self.cap.read()
        #print(f"[grab_frame read] {ret}!!!")
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
        