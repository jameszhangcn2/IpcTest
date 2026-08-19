import cv2
from pathlib import Path
BASE_DIR = Path(__file__).resolve().parent
TEMPLATE_IMG = str(BASE_DIR / ".." / "testTemplate" / "normal.png") # HMI参考模板图
TEMPLATE_SUMMARY_IMG = str(BASE_DIR / ".." / "testTemplate" / "summary.png") # HMI参考模板图
ODOMETER_IMG = str(BASE_DIR / ".." / "testTemplate" / "odometer.png") # HMI局域匹配模板图
SPEEDOMETER_IMG = str(BASE_DIR / ".." / "testTemplate" / "speedometer.png") # HMI局域匹配模板图
TRIPSUMMAR_IMG = str(BASE_DIR / ".." / "testTemplate" / "tripsummary.png") # HMI局域匹配模板图

def pick_roi_by_mouse(image_path):
    """
    鼠标框选图片，输出 roi=(x,y,w,h)
    :param image_path: 截图文件路径
    :return: roi tuple (x,y,w,h) or None
    """
    img = cv2.imread(image_path)
    if img is None:
        raise FileNotFoundError(f"无法读取图片：{image_path}")

    clone = img.copy()
    roi = None
    drawing = False
    start_x, start_y = -1, -1

    def mouse_callback(event, x, y, flags, param):
        nonlocal drawing, start_x, start_y, roi, img
        if event == cv2.EVENT_LBUTTONDOWN:
            drawing = True
            start_x, start_y = x, y
            img = clone.copy()

        elif event == cv2.EVENT_MOUSEMOVE:
            if drawing:
                temp = img.copy()
                cv2.rectangle(temp, (start_x, start_y), (x, y), (0, 255, 0), 2)
                cv2.imshow("Pick ROI(drag mouse, ENTER confirm, ESC exit)", temp)

        elif event == cv2.EVENT_LBUTTONUP:
            drawing = False
            x1 = min(start_x, x)
            y1 = min(start_y, y)
            w = abs(x - start_x)
            h = abs(y - start_y)
            roi = (x1, y1, w, h)
            cv2.rectangle(img, (x1, y1), (x1 + w, y1 + h), (0, 255, 0), 2)
            cv2.imshow("Pick ROI(drag mouse, ENTER confirm, ESC exit)", img)

    cv2.namedWindow("Pick ROI(drag mouse, ENTER confirm, ESC exit)", cv2.WINDOW_NORMAL)
    cv2.setMouseCallback("Pick ROI(drag mouse, ENTER confirm, ESC exit)", mouse_callback)
    cv2.imshow("Pick ROI(drag mouse, ENTER confirm, ESC exit)", img)

    while True:
        key = cv2.waitKey(1) & 0xFF
        if key == 27:  # ESC
            roi = None
            break
        if key == 13:  # ENTER
            break

    cv2.destroyAllWindows()
    return roi


if __name__ == "__main__":
    # ========= 修改成你的截图路径 =========
    pic_path = TEMPLATE_SUMMARY_IMG
    # =====================================

    res_roi = pick_roi_by_mouse(pic_path)
    if res_roi:
        print(f"\n✅ 获取ROI：roi = {res_roi}")
        print(f"# 使用示例：exists, score, pos = template_match_in_roi(img, template, roi={res_roi}, threshold=0.8)")
    else:
        print("❌ 未选择ROI，已退出")