#!/bin/bash
# ════════════════════════════════════════════════════
#  Skills Health Guardian — 一键巡检入口脚本
#  所有参数透传给 cli.py（Python argparse 实现）
# ════════════════════════════════════════════════════
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

# ── 目录验证 ──
if [ ! -f "$SCRIPT_DIR/scanner.py" ]; then
    echo ""
    echo "❌ 错误: scanner.py 未找到"
    echo "   请确保在项目根目录运行此脚本"
    echo ""
    echo "   当前目录: $(pwd)"
    echo "   期望目录: $SCRIPT_DIR"
    echo ""
    echo "💡 正确用法:"
    echo "   $ cd skills-health-guardian"
    echo "   $ ./scripts/health-check.sh --help"
    echo ""
    exit 1
fi

if [ ! -f "$SCRIPT_DIR/cli.py" ]; then
    echo "❌ 错误: cli.py 未找到"
    exit 1
fi

# 检查 Python3
if ! command -v python3 &>/dev/null; then
    echo "❌ 错误: 需要 Python3 才能运行 Skills Health Guardian"
    echo ""
    echo "💡 如何安装 Python3:"
    echo "   • macOS:    brew install python@3.12"
    echo "   • Linux:    sudo apt install python3.12"
    echo "   • Windows:  https://www.python.org/downloads/"
    exit 1
fi

# 检查 Python 版本
PYTHON_VERSION=$(python3 -c 'import sys; print(".".join(map(str, sys.version_info[:2])))' 2>/dev/null || echo "0.0")
if [ "$PYTHON_VERSION" != "0.0" ]; then
    PYTHON_MAJOR=$(echo "$PYTHON_VERSION" | cut -d. -f1)
    PYTHON_MINOR=$(echo "$PYTHON_VERSION" | cut -d. -f2)
    
    if [ "$PYTHON_MAJOR" -lt 3 ] || ([ "$PYTHON_MAJOR" -eq 3 ] && [ "$PYTHON_MINOR" -lt 12 ]); then
        echo "❌ 错误: Python 版本不足 (需要 3.12+)"
        echo "   当前版本: Python $PYTHON_VERSION"
        echo ""
        echo "💡 请升级 Python 后重试"
        exit 1
    fi
fi

# 委托给 cli.py
exec python3 "$SCRIPT_DIR/cli.py" "$@"
