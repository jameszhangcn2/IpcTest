import pywinusb.hid as hid
import time

class HidRelay:
    def __init__(self, vid, pid, report_id):
        f = hid.HidDeviceFilter(vendor_id=vid, product_id=pid)
        self.dev = f.get_devices()[0]
        self.dev.open()
        #self.dev.set_report_id(report_id)

    def set_relay(self, ch: int, enable: bool):
        state = 0x01 if enable else 0x00
        payload = [state, ch, 0,0,0,0,0]
        keyonBytes = [0xa0, 0x06, 0x01, 0xa7, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00]


        self.dev.send_feature_report(keyonBytes)

    def close(self):
        self.dev.close()

if __name__ == "__main__":
    r = HidRelay(0x5131, 0x2007, 0x01)
    r.set_relay(7, True)
    time.sleep(2)
    r.set_relay(7, False)
    r.close()
