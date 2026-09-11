import threading
import queue
import pytest
import time
from datetime import datetime

from utils.serial_logs import format_ts, _multi_match_worker
        
class TestSerialPort:

    def test_multi_keyword(self, serial_bg_monitor):
        keywords = ["BOOT", "READY", "ERROR"]
        result = {}
        log_list = []
        log_lock = threading.Lock()
        stop_event = threading.Event()

        t = threading.Thread(
            target=_multi_match_worker,
            args=(serial_bg_monitor.msg_queue, keywords, result, stop_event, log_list, log_lock),
            daemon=True
        )
        t.start()

        # ==========主线测试逻辑，不被串口监听阻塞==========
        # 例如：发送指令，控制CANoe，等待HMI动作
        # self.send_cmd("reset")

        timeout = 8
        start = time.time()
        found = False
        while time.time() - start < timeout:
            if "READY" in result:
                found = True
                break
            time.sleep(0.1)

        stop_event.set()
        t.join(timeout=1.0)

        # 失败时打印全部捕获串口日志
        with log_lock:
            assert found, f"超时未捕获READY！\n===Captured serial log===\n" + "\n".join(log_list)