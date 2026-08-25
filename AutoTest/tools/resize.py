import cv2

def crop_and_fixed_size(frame, roi_x1, roi_y1, roi_x2, roi_y2, target_w, target_h):
    """
    :param frame: 原始帧
    :param roi_x1,y1,x2,y2: 裁剪坐标
    :param target_w,target_h: 最终输出宽高
    :return: 输出帧（固定target_w × target_h）
    """
    # 裁剪ROI
    crop_img = frame[roi_y1:roi_y2, roi_x1:roi_x2]
    h_crop, w_crop = crop_img.shape[:2]

    # 等比例缩放，不超出目标画布
    scale = min(target_w / w_crop, target_h / h_crop)
    new_w = int(w_crop * scale)
    new_h = int(h_crop * scale)
    scaled = cv2.resize(crop_img, (new_w, new_h), interpolation=cv2.INTER_AREA)

    # 黑色画布
    canvas = cv2.resize(crop_img, (target_w, target_h)) * 0
    # 居中放置
    off_x = (target_w - new_w) // 2
    off_y = (target_h - new_h) // 2
    canvas[off_y:off_y+new_h, off_x:off_x+new_w] = scaled
    return canvas

# =========配置=========
VIDEO_PATH = "VID_20260824_101714.mp4"
ROI_X1, ROI_Y1 = 420, 0
ROI_X2, ROI_Y2 = 1720, 1080
OUT_W, OUT_H = 1280, 960
OUT_VIDEO_PATH = "testout.mp4"
# =====================

cap = cv2.VideoCapture(VIDEO_PATH)
fps = cap.get(cv2.CAP_PROP_FPS)
fourcc = cv2.VideoWriter_fourcc(*'mp4v')
vw = cv2.VideoWriter(OUT_VIDEO_PATH, fourcc, fps, (OUT_W, OUT_H))

while cap.isOpened():
    ret, frame = cap.read()
    if not ret:
        break
    out_frame = crop_and_fixed_size(frame, ROI_X1, ROI_Y1, ROI_X2, ROI_Y2, OUT_W, OUT_H)
    vw.write(out_frame)
    cv2.imshow("result", out_frame)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
vw.release()
cv2.destroyAllWindows()