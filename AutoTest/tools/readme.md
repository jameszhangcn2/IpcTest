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

```
