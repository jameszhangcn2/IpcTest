#python   
import cv2
 
# 0 代表本机第一个摄像头；USB外接摄像头尝试 1,2
cap = cv2.VideoCapture(1)
 
# 设置分辨率（可选）
cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)
 
count = 0
 
while True:
    ret, frame = cap.read()
    if not ret:
        print("读取摄像头失败，请检查设备")
        break
 
    cv2.imshow("Camera", frame)
 
    key = cv2.waitKey(1) & 0xFF
    if key == ord('s'):
        # 按下 s 截图保存
        filename = f"camera_{count}.jpg"
        cv2.imwrite(filename, frame)
        print(f"已保存 {filename}")
        count += 1
    elif key == 27:
        # ESC退出
        break
 
cap.release()
cv2.destroyAllWindows()