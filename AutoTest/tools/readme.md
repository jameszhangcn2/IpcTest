# tools used for auto test

```
# 单个文件
pytest --can-log=your_log.asc -v

# 批量目录
pytest --can-log-dir=./logs/ --output=./reports/ -v

# 指定波特率和帧数阈值
pytest --can-log=log.asc --baudrate=250000 --min-frames=100 -v


python run_analysis.py your_log.asc -o output.xlsx
python run_analysis.py --dir ./logs/ -o ./reports/

# pytest 方式
pytest --can-log=your_log.asc --dbc=your_db.dbc -v

# 命令行脚本方式
python run_analysis.py your_log.asc --dbc=your_db.dbc -o output.xlsx

```
```
## Excel 报告包含 5 个 Sheet

表格

| Sheet | 内容 |
| --- | --- |
| **概览** | 总帧数、唯一 ID 数、错误帧数、时长、各通道摘要 |
| **报文统计** | 每 ID 的帧数 / 平均周期 / 最小最大周期 / 抖动 / 频率 / 数据变化率 |
| **通道统计** | 每通道帧数 / Tx-Rx 分布 / 平均帧率 / 估算总线负载 |
| **错误帧** | 所有 ErrorFrame 的时间戳和通道 |
| **原始数据摘要** | 每 ID 最多采样 10 帧原始 Hex 数据 |

## 核心特性

- 支持 Vector `.asc`（CANoe 原生）、Peak `.log`、candump 格式
- 自动识别标准帧 / 扩展帧 / 远程帧 / 错误帧
- 周期分析：平均 / 最小 / 最大 / 抖动（标准差）
- 总线负载估算（可指定波特率）
- pytest 参数化：一个命令批量分析整个目录，每个文件独立测试用例
- 纯 Python 解析器，不依赖 python-can，Windows/Linux 均可直接运行

示例报告已基于 `sample.asc` 生成，可直接打开查看效果。把你的 `.asc` 文件路径传入 `--can-log` 参数即可分析真实日志。
```



```
> 
> 红米 DroidCam 拍摄反光大，优先用 `blur_ksize=7`

2. **canny_low /canny_high 边缘检测**

- 差值一般保持大约 1:3 关系，例如 `12 / 50`、`20 /70`
- 完全看不到屏幕边框（识别不到四边形）：**两个数值同时往小调**，灵敏度升高
`canny_low=8, canny_high=35`
- 画面一堆杂乱噪点边缘：**两个数值同时调大**，降低灵敏度
`canny_low=25, canny_high=80`

> 
> 口诀：**识别不到，数值减小；噪点太多，数值加大**

3. **area_min_ratio 最小轮廓面积过滤**
`area < height * width * area_min_ratio`

- 屏幕占画面很小：调小，`0.02`
- 很多小杂物轮廓干扰：调大，`0.06~0.08`

4. **poly_epsilon 多边形拟合 `approxPolyDP`**
`approx = cv2.approxPolyDP(cnt, poly_epsilon * peri, True)`

- 屏幕轮廓弯曲、不规整、不是完美四边形 → **调大 0.03‑0.04**，允许轮廓误差更大
- 轮廓很标准方正 → `0.02`

> 
> 现象：明明是四边形，但是 `len(approx)≠4`，就加大这个值。

5. **dilate_kernel /dilate_iter 膨胀，把断开边框连起来**

```
kernel = np.ones((dilate_kernel, dilate_kernel), np.uint8)
edges_dilate = cv2.dilate(edges, kernel, iterations=dilate_iter)
```

- 屏幕边框边缘断断续续不闭合：调大 kernel 或者调大迭代次数
`dilate_kernel=9, dilate_iter=3`
- 边缘糊成一大块：调小，`kernel=7, iter=2`

---

# 两套现成参数模板，直接复制使用

## 模板 A：反光重、边框弱（红米 DroidCam 最常用）✅

```
corners = find_hmi_screen_rect(frame,
    blur_ksize=7,
    canny_low=12,
    canny_high=50,
    area_min_ratio=0.04,
    poly_epsilon=0.03,
    dilate_kernel=9,
    dilate_iter=3
)
```

## 模板 B：画面干净，边框清晰

```
corners = find_hmi_screen_rect(frame,
    blur_ksize=5,
    canny_low=20,
    canny_high=70,
    area_min_ratio=0.05,
    poly_epsilon=0.02,
    dilate_kernel=7,
    dilate_iter=2
)
```

# 调参调试流程（标准排查步骤）

1. **开启 Debug 输出，保存中间图片**
在函数末尾保存三张图：gray、edges、edges_dilate

```
cv2.imwrite("debug_gray.jpg", gray)
cv2.imwrite("debug_edges.jpg", edges)
cv2.imwrite("debug_dilate.jpg", edges_dilate)
```

打开图片肉眼观察：

### 情况 1：debug_edges.jpg，屏幕一圈闭合黑线清晰可见

> 
> 边缘已经出来，问题在轮廓 / 多边形过滤

- 优先调大 `poly_epsilon`
- 调小 `area_min_ratio`

### 情况 2：debug_edges.jpg，屏幕边框断断续续，有缺口

> 
> 边缘不闭合

- 加大 `dilate_kernel`、`dilate_iter`，把缺口连起来

### 情况 3：debug_edges.jpg，几乎看不到屏幕边框，一片黑

> 
> Canny 没有提取边框

- `canny_low、canny_high` 同时减小；适度减小 blur_ksize

### 情况 4：debug_edges.jpg 整张图密密麻麻全是白线（反光噪点）

> 
> 反光严重，大量虚假边缘

- 增大 `blur_ksize`（9），把反光抹平
- `canny_low、canny_high` 数值加大，降低灵敏度

### 情况 5：edges 图全是边缘，膨胀后直接铺满整张图片

> 
> 降级 Canny‑ROI 会返回整张画面，触发 ROI>0.92 保护返回 None

- 增大 Canny 阈值，增加模糊；**优先物理改善拍摄角度消除反光，软件调参有上限**

# 调参优先级顺序（不要乱改）

1️⃣ 先看 debug 三张图片，判断属于上面哪一类
2️⃣ 优先调：`blur_ksize` 和 `canny_low/canny_high`（影响最大）
3️⃣ 其次调：膨胀 `dilate_kernel / dilate_iter`
4️⃣ 再调：`poly_epsilon` 多边形拟合
5️⃣ 最后调面积阈值 `area_min_ratio`

> 
> 不要一次改一堆参数，一次只改 1‑2 个，运行看 debug 图效果。

# 识别还是不行的兜底策略

四边形检测无论怎么调参都返回 None：

- 悬浮屏没有物理边框，Canny 找不到四边形，属于硬件限制。
- 代码自动走到 Canny 包围盒 ROI；包围盒失效，使用整张原图 1280×720 兜底输出。

# 物理拍摄优先（软件调参救不了）

1. 摄像头角度避开屏幕反光；反光是头号杀手
2. 不要全黑环境，要有环境光，让**屏幕物理边框显现出来**，而不是只拍到发光 UI
3. HMI 屏幕不要占满整张画面，四周留一点背景，方便轮廓算法识别

```
