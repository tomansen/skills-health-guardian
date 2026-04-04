#!/bin/bash
# Skills Health Guardian - 一键巡检脚本
# 快速扫描所有 skills 的环境健康状态
# 用法: ./health-check.sh [--json] [--fix] [--output report.md]

set -euo pipefail

SKILLS_DIR="${HOME}/.workbuddy/skills"
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
REPORT_DIR="${HOME}/.workbuddy/skills/skills-health-guardian/reports"
mkdir -p "${REPORT_DIR}"

# 解析参数
MODE="report"  # report | check | fix
OUTPUT_FORMAT=""
DRY_RUN=true
TARGET=""
FIX_TYPE=""

while [[ $# -gt 0 ]]; do
    case "$1" in
        --json) OUTPUT_FORMAT="json"; shift ;;
        --fix|--repair)
            MODE="fix"
            FIX_TYPE="${2:-runtime}"
            TARGET="${3:-}"
            shift 2 || true
            ;;
        --yes|-y) DRY_RUN=false; shift ;;
        --dry-run) DRY_RUN=true; shift ;;
        --check) MODE="check"; shift ;;
        env-template|env_template)
            MODE="env"
            shift
            ;;
        -o|--output) OUTPUT_FILE="$2"; shift 2 ;;
        --path) SKILLS_DIR="$2"; shift 2 ;;
        *) echo "未知参数: $1"; exit 1 ;;
    esac
done

# 检查 Python3
if ! command -v python3 &>/dev/null; then
    echo "❌ 需要安装 Python3 才能运行扫描器"
    exit 1
fi

echo "🏥 Skills 环境健康管家"
echo "═══════════════════════════════"
echo ""

case "$MODE" in
    report|check)
        if [ "$MODE" = "check" ]; then
            python3 "${SCRIPT_DIR}/fixer.py" check --path "${SKILLS_DIR}"
            exit $?
        fi

        # 报告模式：先扫描再生成报告
        SCAN_ARGS="--path ${SKILLS_DIR}"
        [ -n "$OUTPUT_FORMAT" ] && SCAN_ARGS="$SCAN_ARGS --${OUTPUT_FORMAT}"
        [ -n "$OUTPUT_FILE" ] && SCAN_ARGS="$SCAN_ARGS -o ${OUTPUT_FILE}"

        # 运行 reporter（内部会调用 scanner）
        python3 "${SCRIPT_DIR}/scanner.py" ${SCAN_ARGS}
        ;;

    fix)
        FIX_ARGS="fix ${FIX_TYPE} ${TARGET} --path ${SKILLS_DIR}"
        $DRY_RUN && FIX_ARGS="$FIX_ARGS --dry-run"

        python3 "${SCRIPT_DIR}/fixer.py" ${FIX_ARGS}
        ;;

    env)
        python3 "${SCRIPT_DIR}/fixer.py" env-template --path "${SKILLS_DIR}" ${OUTPUT_FILE:+-o $OUTPUT_FILE}
        ;;

    *)
        echo "用法: $0 [--check|--fix TYPE TARGET] [--json] [--output FILE]"
        echo ""
        echo "命令:"
        echo "  (无参数)   运行完整健康报告"
        echo "  --check    仅检查可修复项"
        echo "  --fix TYPE TARGET  执行修复 (runtime/deps/env_template/isolate)"
        echo "  env-template     生成环境变量模板"
        echo ""
        echo "选项:"
        echo "  --json       JSON 格式输出"
        echo "  --dry-run    仅预览不执行"
        echo "  --yes, -y    跳过确认直接执行"
        echo "  --output F   指定输出文件路径"
        exit 1
        ;;
esac
