import subprocess
from pathlib import Path
from datetime import datetime

def build_session_log_dir():
    # 和你 dir_session fixture 一模一样的创建逻辑
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    log_root = Path("./testlogs")
    session_dir = log_root / f"session_{timestamp}"
    session_dir.mkdir(parents=True, exist_ok=True)
    return session_dir

if __name__ == "__main__":
    session_dir = build_session_log_dir()
    html_file = session_dir / "test_report.html"

    cmd = [
        "python", "-m", "pytest",
        "./tests/testHmi.py", "-v", "-s",
        "--html", str(html_file),
        "--self-contained-html",
        "--log-root", str(session_dir)
    ]
    print(f"HTML报告目标路径：{html_file}")
    subprocess.run(cmd)