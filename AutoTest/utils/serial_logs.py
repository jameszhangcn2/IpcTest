import serial
import threading
import queue
from datetime import datetime
import time
from collections import deque
from pathlib import Path
import zipfile
def format_ts(ts: float) -> str:
    """unix时间戳 -> YYYY-MM-DD HH:MM:SS.sss"""
    dt = datetime.fromtimestamp(ts)
    return dt.strftime("%Y-%m-%d %H:%M:%S.%f")[:-3]

def _multi_match_worker(msg_queue: queue.Queue, target_list: list[str], result_dict: dict, stop_event: threading.Event, log_list: list, lock: threading.Lock):
    while not stop_event.is_set():
        try:
            ts, raw = msg_queue.get(timeout=0.2)
            line_text = raw.decode("utf-8", errors="replace")
            ts_str = format_ts(ts)
            #print(f"[{ts_str}] RX: {line_text.strip()}")

            # 线程安全存入全部日志
            with lock:
                log_list.append(f"[{ts_str}] {line_text.strip()}")

            # 关键词匹配
            for keyword in target_list:
                if keyword in line_text and keyword not in result_dict:
                    result_dict[keyword] = (ts, line_text)
                    print(f"[{ts_str}] ✅ HIT keyword: {keyword}")
            msg_queue.task_done()
        except queue.Empty:
            continue
        except Exception as e:
            now_str = format_ts(time.time())
            print(f"[{now_str}] MATCH WORKER ERR: {e}")

class SerialBgMonitor:
    def __init__(
        self,
        port,
        baudrate=115200,
        max_cache=2000,
        log_file=None,
        max_file_size_mb=20,
        max_backup_count=5,
        write_queue_maxsize=500,
        # 队列水位监控配置
        monitor_interval = 1.0,
        msg_queue_warn_thresh = 200,
        write_queue_warn_thresh = 400,
        rotate_queue_warn_thresh = 2
    ):
        self.port = port
        self.baudrate = baudrate
        self.ser = None

        # 1. 给pytest用例消费的串口消息队列
        self.msg_queue = queue.Queue()
        # 环形缓存，检索历史日志
        self.log_cache = deque(maxlen=max_cache)
        self.cache_lock = threading.Lock()
        self.stop_event = threading.Event()

        # 2. 文件写入队列（独立写线程）
        self.write_queue = queue.Queue(maxsize=write_queue_maxsize)
        # 3. 日志轮转任务队列（独立轮转线程）
        self.rotate_task_queue = queue.Queue(maxsize=2)

        # log rotate config
        self.log_file_path = Path(log_file) if log_file else None
        self.max_file_size = max_file_size_mb * 1024 * 1024
        self.max_backup_count = max_backup_count
        self.fd = None
        self.current_file_size = 0

        self.file_write_thread = None
        self.rotate_thread = None
        # 水位监控线程
        self.queue_monitor_thread = None
        self.monitor_interval = monitor_interval
        self.msg_queue_warn_thresh = msg_queue_warn_thresh
        self.write_queue_warn_thresh = write_queue_warn_thresh
        self.rotate_queue_warn_thresh = rotate_queue_warn_thresh

        if self.log_file_path:
            self.log_file_path.parent.mkdir(parents=True, exist_ok=True)
            self._open_new_logfile()
            # 启动文件写线程
            self.file_write_thread = threading.Thread(target=self._file_write_worker, daemon=True)
            self.file_write_thread.start()
            # 启动轮转worker
            self.rotate_thread = threading.Thread(target=self._rotate_worker, daemon=True)
            self.rotate_thread.start()
            # 启动队列水位监控线程
            self.queue_monitor_thread = threading.Thread(target=self._queue_monitor_worker, daemon=True)
            self.queue_monitor_thread.start()

    def _open_new_logfile(self):
        self.fd = open(self.log_file_path, "a", encoding="utf-8", errors="replace")
        if self.log_file_path.exists():
            self.current_file_size = self.log_file_path.stat().st_size
        else:
            self.current_file_size = 0

    def _rotate_worker(self):
        """独立轮转线程：重命名、zip压缩、清理旧包"""
        while not self.stop_event.is_set():
            try:
                _ = self.rotate_task_queue.get(timeout=0.5)
                if self.fd:
                    self.fd.close()
                    self.fd = None

                ts = time.strftime("%Y%m%d_%H%M%S")
                backup_name = f"{self.log_file_path.stem}_{ts}{self.log_file_path.suffix}"
                backup_path = self.log_file_path.parent / backup_name

                self.log_file_path.replace(backup_path)
                zip_path = backup_path.with_suffix(".zip")
                with zipfile.ZipFile(zip_path, "w", compression=zipfile.ZIP_DEFLATED) as zf:
                    zf.write(backup_path, arcname=backup_path.name)
                backup_path.unlink(missing_ok=True)

                # 清理旧压缩包
                zip_list = sorted(
                    self.log_file_path.parent.glob(f"{self.log_file_path.stem}_*.zip"),
                    key=lambda p: p.stat().st_mtime
                )
                if len(zip_list) > self.max_backup_count:
                    for old_zip in zip_list[:-self.max_backup_count]:
                        old_zip.unlink(missing_ok=True)

                # 重新打开新日志文件
                self._open_new_logfile()
                self.rotate_task_queue.task_done()
            except queue.Empty:
                continue
            except Exception as e:
                now_str = format_ts(time.time())
                print(f"[{now_str}] [ROTATE_WORKER ERR] {e}")
                time.sleep(0.2)

    def _file_write_worker(self):
        """独立文件写入线程：负责写文件、统计字节、触发轮转"""
        while not self.stop_event.is_set():
            try:
                line_str = self.write_queue.get(timeout=0.3)
                if self.fd:
                    self.fd.write(line_str)
                    self.fd.flush()
                    line_bytes = len(line_str.encode("utf-8"))
                    self.current_file_size += line_bytes
                    # 判断达到阈值，投递轮转任务
                    if self.current_file_size >= self.max_file_size:
                        try:
                            self.rotate_task_queue.put_nowait(1)
                        except queue.Full:
                            now_str = format_ts(time.time())
                            print(f"[{now_str}] WARN: rotate task queue full, skip rotate trigger")
                self.write_queue.task_done()
            except queue.Empty:
                continue
            except Exception as e:
                now_str = format_ts(time.time())
                print(f"[{now_str}] [FILE_WRITE_WORKER ERR] {e}")
                time.sleep(0.2)

    def _queue_monitor_worker(self):
        """队列水位监控线程，定时打印队列size + 告警"""
        while not self.stop_event.is_set():
            try:
                msg_q_size = self.msg_queue.qsize()
                write_q_size = self.write_queue.qsize()
                rotate_q_size = self.rotate_task_queue.qsize()
                now_str = format_ts(time.time())

                log_str = f"[{now_str}] [QUEUE_MONITOR] msg_q:{msg_q_size}, write_q:{write_q_size}, rotate_q:{rotate_q_size}"
                warn_list = []
                if msg_q_size >= self.msg_queue_warn_thresh:
                    warn_list.append(f"msg_queue high({msg_q_size})")
                if write_q_size >= self.write_queue_warn_thresh:
                    warn_list.append(f"write_queue high({write_q_size})")
                if rotate_q_size >= self.rotate_queue_warn_thresh:
                    warn_list.append(f"rotate_queue high({rotate_q_size})")

                if warn_list:
                    log_str += " | WARN: " + ", ".join(warn_list)
                print(log_str)

                time.sleep(self.monitor_interval)
            except Exception as e:
                now_str = format_ts(time.time())
                print(f"[{now_str}] [QUEUE_MONITOR ERR] {e}")
                time.sleep(0.5)

    def _read_task(self):
        """串口读取线程：只收串口数据，入队，完全无磁盘IO"""
        while not self.stop_event.is_set():
            try:
                raw = self.ser.readline()
                if not raw:
                    continue
                ts = time.time()
                ts_str = format_ts(ts)
                text = raw.decode("utf-8", errors="replace").strip("\r\n")
                line_str = f"[{ts_str}] {text}\n"

                # 1. 推入pytest消息队列（保留原始ts和raw，用例可以自己格式化）
                self.msg_queue.put((ts, raw))
                # 2. 存入环形缓存
                with self.cache_lock:
                    self.log_cache.append((ts, raw))
                # 3. 投递到文件写队列
                try:
                    self.write_queue.put_nowait(line_str)
                except queue.Full:
                    print(f"[{ts_str}] WARN: serial write_queue full! drop log line: {text.strip()}")

            except Exception as e:
                err_ts = time.time()
                err_ts_str = format_ts(err_ts)
                err_msg = f"[{err_ts_str}] SERIAL_READ_ERR: {e}\n"
                print(err_msg)
                try:
                    self.write_queue.put_nowait(err_msg)
                except queue.Full:
                    print(f"[{err_ts_str}] WARN: write_queue full, drop error log: {e}")
                time.sleep(0.05)

    def start(self):
        self.ser = serial.Serial(self.port, self.baudrate, timeout=0.1)
        self.stop_event.clear()
        self.thread = threading.Thread(target=self._read_task, daemon=True)
        self.thread.start()

    def stop(self):
        self.stop_event.set()
        # 等待串口读线程退出
        if hasattr(self, "thread") and self.thread:
            self.thread.join(timeout=1.5)

        # 等待写队列全部写完
        if self.file_write_thread:
            self.write_queue.join()
            self.file_write_thread.join(timeout=1.5)

        # 等待轮转任务执行完成
        if self.rotate_thread:
            self.rotate_task_queue.join()
            self.rotate_thread.join(timeout=1.5)

        # 等待监控线程退出
        if self.queue_monitor_thread:
            self.queue_monitor_thread.join(timeout=1.0)

        if self.ser and self.ser.is_open:
            self.ser.close()
        if self.fd:
            self.fd.close()
            self.fd = None

    def search_cache(self, target: str) -> bool:
        with self.cache_lock:
            for ts, raw in self.log_cache:
                text = raw.decode("utf-8", errors="replace")
                if target in text:
                    return True
        return False

    def dump_cache_logs(self) -> str:
        lines = []
        with self.cache_lock:
            for ts, raw in self.log_cache:
                ts_str = format_ts(ts)
                text = raw.decode("utf-8", errors="replace")
                lines.append(f"[{ts_str}] {text.strip()}")
        return "\n".join(lines)