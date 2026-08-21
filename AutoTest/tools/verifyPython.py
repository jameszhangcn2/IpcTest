import win32com.client
import pythoncom

def test_canoe_com_64bit():
    pythoncom.CoInitialize()
    app = win32com.client.Dispatch("CANoe.Application")
    print("/n James")
    print(f"CANoe 版本: {app.Version}")
    print("Python 位数: 64位，COM 调用正常")
    app.Visible = True
    pythoncom.CoUninitialize()

if __name__ == "__main__":
    test_canoe_com_64bit()