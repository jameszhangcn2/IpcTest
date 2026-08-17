import pywinusb.hid as hid
import time
def scan_hid():
    all_devs = hid.find_all_hid_devices()
    for dev in all_devs:
        print(f"VID:0x{dev.vendor_id:04X} PID:0x{dev.product_id:04X} | {dev.product_name}")
        dev.close()



VID = 0x5131
PID = 0x2007

def send_hid_feature_64(dev, cmd_data):
    """
    发送64字节 Feature Report
    :param dev: 已open的HidDevice
    :param cmd_data: 有效载荷list
    """
    report_id = 0x00   # 设备无ReportID就填0
    #frame = [report_id] + cmd_data
    frame = cmd_data

    # 填充0直到总长度 = 64
    if len(frame) < 64:
        frame += [0x00] * (64 - len(frame))
    elif len(frame) > 64:
        frame = frame[:64]

    dev.send_feature_report(frame)
    print(f"发送Feature帧({len(frame)}字节): {frame}")
    
if __name__ == "__main__":
    scan_hid()
    filter_dev = hid.HidDeviceFilter(vendor_id=VID, product_id=PID)
    device_list = filter_dev.get_devices()
    if not device_list:
        print("未找到HID设备")
    else:
        dev = device_list[0]
        dev.open()

        # 你的有效指令，例如 [0x01,0x02,0x03,0x04]
        payload = [0xa0, 0x06, 0x00, 0xa6]
        send_hid_feature_64(dev, payload)
        time.sleep(10)
        dev.close()

    