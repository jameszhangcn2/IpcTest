import pythoncom
import win32com.client
import time
import os
import subprocess

def kill_canoe_process():
    try:
        subprocess.run(["taskkill", "/F", "/IM", "CANoe64.exe"], capture_output=True, shell=False)
        time.sleep(1.5)
    except Exception:
        pass

def test_canoe_capl_sysvar():
    pythoncom.CoInitialize()
    app = None
    cfg_path = r"C:\autoTest\test.cfg"
    assert os.path.exists(cfg_path)
    kill_canoe_process()

    try:
        app = win32com.client.Dispatch("CANoe.Application")
        app.Visible = True
        time.sleep(1.2)

        app.Open(cfg_path)
        time.sleep(10)

        print(f"Loaded config: {app.Configuration.Name}")
        func1 = app.CAPL.GetFunction("TestFunc")
        result = func1.Call()
        
        SetSysVarLong =  app.CAPL.GetFunction("SetSysVarLong")
        # --------调用CAPL导出函数读写系统变量 Env::Sys_Test (int)--------
        ret_code = SetSysVarLong.Call("AutoTest", "var1", 88)
        print(f"SetSysVarLong return code={ret_code}")
        GetSysVarLong =  app.CAPL.GetFunction("GetSysVarLong")
        read_val = GetSysVarLong.Call("AutoTest", "var1")
        print(f"Read Sys_Test = {read_val}")

    except Exception as e:
        print(f"Error: {e}")
        raise
    finally:
        if app is not None:
            app.Quit()
        pythoncom.CoUninitialize()
        kill_canoe_process()