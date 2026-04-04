#!/bin/bash
# ════════════════════════════════════════════════════════
#  Skills Health Guardian — 一键巡检入口脚本
#  所有参数透传给 cli.py（Python argparse 实现）
# ════════════════════════════════════════════════════════
#
# 用法:
#   ./health-check.sh                     # 默认彩色表格输出
#   ./health-check.sh --format json       # JSON 输出
#   ./health-check.sh --format quiet      # 单行摘要
#   ./health-check.sh -o report.md        # 保存报告
#   ./health-check.sh --watch 30          # 每30秒刷新
#   ./health-check.sh --help              # 查看完整帮助

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"

# 检查 Python3
if ! command -v python3 &>/dev/null; then
    echo "❌ 需要安装 Python3 才能运行 Skills Health Guardian"
    exit 1
fi

# 委托给 cli.py
exec python3 "$SCRIPT_DIR/cli.py" "$@"
