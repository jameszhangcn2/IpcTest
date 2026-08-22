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
