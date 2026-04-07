#!/usr/bin/env python3
# ruff: noqa: E402 (module level import not at top - needed for sys.path manipulation)
"""
Skills Health Guardian CLI — 统一命令行入口
提供彩色终端输出、多格式报告、Watch 模式、自定义输出路径等功能。

用法:
    python3 cli.py                     # 默认 table 格式（带颜色）
    python3 cli.py --format json       # JSON 输出
    python3 cli.py --format markdown   # Markdown 完整报告
    python3 cli.py --format quiet      # 仅一行摘要
    python3 cli.py --watch 30          # 每 30 秒刷新
    python3 cli.py -o report.md        # 保存到文件
    python3 cli.py --skip-fix         # 跳过修复步骤
    python3 cli.py -v                 # 详细输出
"""

import sys
import os
import json
import time
import argparse
from pathlib import Path

# 确保能 import 同目录下的模块
SCRIPT_DIR = Path(__file__).resolve().parent
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

from scanner import SkillsScanner
from reporter import HealthReporter, ReportConfig


# ════════════════════════════════════════════════════════
#  彩色输出工具
# ════════════════════════════════════════════════════════

class Colors:
    """ANSI 颜色码"""
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    BOLD = '\033[1m'
    DIM = '\033[2m'
    CYAN = '\033[96m'
    MAGENTA = '\033[95m'
    END = '\033[0m'


def colorize(text: str, color: str) -> str:
    """给文本着色（自动检测是否支持颜色）"""
    if os.environ.get('NO_COLOR') or not sys.stdout.isatty():
        return text
    return f"{color}{text}{Colors.END}"


def status_icon(score: int) -> str:
    """根据分数返回状态图标和颜色字符串"""
    if score >= 80:
        return colorize("✅ Healthy", Colors.GREEN)
    elif score >= 50:
        return colorize("⚠️ Warning", Colors.YELLOW)
    else:
        return colorize("🔴 Error  ", Colors.RED)


def score_color_str(score: int) -> str:
    """带颜色的分数字符串"""
    if score >= 80:
        return colorize(f"{score}/100", Colors.GREEN)
    elif score >= 50:
        return colorize(f"{score}/100", Colors.YELLOW)
    else:
        return colorize(f"{score}/100", Colors.RED)


# ════════════════════════════════════════════════════════
#  Table 格式输出（Unicode 边框表格）
# ════════════════════════════════════════════════════════

def format_table(scanner: SkillsScanner, verbose: bool = False) -> str:
    """生成漂亮的 Unicode 表格格式的健康报告"""
    summary = scanner.get_summary()
    lines: list[str] = []

    # ── 标题区域 ──
    title = "🏥 Skills Health Guardian v1.0.0"
    box_width = 56

    lines.append("╔" + "═" * (box_width - 2) + "╗")
    # 居中标题
    title_padding = (box_width - 2 - len(title.encode('gbk')) // 2 * 2 - len(title)) // 2  # rough center
    lines.append("║" + " " * max(4, title_padding) + title + " " * max(4, box_width - 2 - max(4, title_padding) - len(title) - 1) + "║")
    lines.append("╠" + "═" * (box_width - 2) + "╣")

    # ── 摘要行 ──
    avg = summary['avg_health_score']
    avg_display = f"{avg:.1f}/100"
    if avg >= 80:
        avg_status = "✅ HEALTHY "
    elif avg >= 50:
        avg_status = "⚠️ WARNING "
    else:
        avg_status = "🔴 CRITICAL"

    scan_time_short = summary.get('scan_time', '')[:19].replace('T', ' ')

    line1 = f"║  Global Health Score: {avg_display:>7} {avg_status}     ║"
    lines.append(line1)
    line2 = f"║  Scanned: {summary['total_skills']:>3} skills | Time: {scan_time_short}  ║"
    lines.append(line2)

    # ── 表头分隔 ──
    lines.append("╠" + "════════" + "╬" + "═══════" + "╬" + "═══════" + "╬" + "══════════════════" + "╣")
    lines.append("║ Status    ║ Score  ║ Issues ║ Skill Name              ║")
    lines.append("╠" + "════════" + "╬" + "═══════" + "╬" + "═══════" + "╬" + "══════════════════" + "╣")

    # ── 各 skill 行 ──
    sorted_skills = sorted(scanner.skills.items(), key=lambda x: x[1].health_score, reverse=True)

    for name, report in sorted_skills:
        score = report.health_score
        issues_count = len(report.issues)
        warnings_count = len(report.warnings)
        total_issues = issues_count + warnings_count

        # 状态列
        if score >= 80:
            status = colorize(" ✅ OK    ", Colors.GREEN)
        elif score >= 50:
            status = colorize(" ⚠️ WARN   ", Colors.YELLOW)
        else:
            status = colorize(" 🔴 ERR    ", Colors.RED)

        # 分数列
        sc = f"{score:>3}/{100}"

        # 截断名称（最大 24 字符）
        name_display = name[:24].ljust(24)

        row = f"║{status}║ {sc} ║ {total_issues:>5} ║ {name_display} ║"
        lines.append(row)

        # verbose 模式显示详情
        if verbose:
            if report.issues:
                for issue in report.issues[:3]:
                    issue_line = f"║          ║       ║   ❌ {issue[:44]:<44} ║"
                    lines.append(issue_line)
            if report.warnings:
                for warn in report.warnings[:2]:
                    warn_line = f"║          ║       ║   ⚠️  {warn[:43]:<43} ║"
                    lines.append(warn_line)
            if report.dependencies and verbose:
                deps_short = [d.name for d in report.dependencies[:4]]
                dep_str = ", ".join(deps_short)
                if len(report.dependencies) > 4:
                    dep_str += f" (+{len(report.dependencies)-4})"
                dep_line = f"║          ║       ║   📦 Deps: {dep_str[:40]:<40} ║"
                lines.append(dep_line)

    lines.append("╚" + "════════" + "╩" + "═══════" + "╩" + "═══════" + "╩" + "══════════════════" + "╝")

    # ── 底部统计 ──
    lines.append("")
    healthy_c = summary['healthy_count']
    warning_c = summary['warning_count']
    critical_c = summary['critical_count']

    stats_line = (
        f"  Total: {summary['total_skills']} | "
        f"{colorize(f'Healthy: {healthy_c}', Colors.GREEN)} | "
        f"{colorize(f'Warning: {warning_c}', Colors.YELLOW)} | "
        f"{colorize(f'Critical: {critical_c}', Colors.RED)} | "
        f"Deps: {summary.get('total_dependencies', 0)}"
    )
    lines.append(stats_line)

    if summary.get('global_issues'):
        lines.append("")
        lines.append(colorize(f"  ⚡ Global Issues: {len(summary['global_issues'])}", Colors.YELLOW))
        for issue in summary['global_issues'][:3]:
            if issue['type'] == 'version_conflict':
                lines.append(f"     • Version conflict: {issue['dependency']}")
            elif issue['type'] == 'heavy_runtime_dependency':
                lines.append(f"     • Heavy runtime: {issue['runtime']} used by {issue['count']} skills")

    return "\n".join(lines)


# ════════════════════════════════════════════════════════
#  Quiet 格式输出（单行摘要）
# ════════════════════════════════════════════════════════

def format_quiet(scanner: SkillsScanner) -> str:
    """仅输出一行摘要"""
    summary = scanner.get_summary()
    avg = summary['avg_health_score']
    ts = summary.get('scan_time', '')[:19].replace('T', ' ')
    return (
        f"[{ts}] SHG score={avg:.1f} "
        f"ok={summary['healthy_count']} "
        f"warn={summary['warning_count']} "
        f"crit={summary['critical_count']} "
        f"total={summary['total_skills']}"
    )


# ════════════════════════════════════════════════════════
#  JSON 格式输出
# ════════════════════════════════════════════════════════

def format_json_output(scanner: SkillsScanner) -> str:
    """输出结构化 JSON"""
    summary = scanner.get_summary()
    data = {
        "version": "1.0.0",
        "generator": "skills-health-guardian",
        "scan_time": summary.get('scan_time', ''),
        "summary": {
            "total_skills": summary['total_skills'],
            "avg_health_score": summary['avg_health_score'],
            "healthy": summary['healthy_count'],
            "warning": summary['warning_count'],
            "critical": summary['critical_count'],
            "total_dependencies": summary.get('total_dependencies', 0),
        },
        "skills": {}
    }
    for name, report in scanner.skills.items():
        data["skills"][name] = {
            "health_score": report.health_score,
            "status": "healthy" if report.health_score >= 80 else "warning" if report.health_score >= 50 else "critical",
            "dependencies": [d.__dict__ if hasattr(d, '__dict__') else {'name': getattr(d, 'name', '?')} for d in report.dependencies],
            "issues": report.issues,
            "warnings": report.warnings,
            "runtime_requirements": report.runtime_requirements,
            "env_vars": report.env_vars,
        }
    if summary.get('global_issues'):
        data["global_issues"] = summary['global_issues']

    return json.dumps(data, ensure_ascii=False, indent=2)


# ════════════════════════════════════════════════════════
#  Markdown 格式输出（调用 reporter）
# ════════════════════════════════════════════════════════

def format_markdown_output(scanner: SkillsScanner, output_dir: str = "") -> str:
    """生成完整 Markdown 报告"""
    scan_data = {
        "summary": scanner.get_summary(),
        "skills": {
            n: r.__dict__ if hasattr(r, '__dict__') else r
            for n, r in scanner.skills.items()
        }
    }
    reporter = HealthReporter(output_dir)
    config = ReportConfig(format="markdown", include_trend=False)
    return reporter.generate(scan_data, config)


# ════════════════════════════════════════════════════════
#  Watch 模式
# ════════════════════════════════════════════════════════

def run_watch_mode(args):
    """持续监控模式 — 定期重新扫描"""
    interval = args.watch_interval
    max_count = args.watch_count or 0  # 0 = 无限
    count = 0

    # 使用 ANSI 清屏实现刷新效果
    clear_cmd = "\033[2J\033[H"

    while True:
        count += 1
        if max_count > 0 and count > max_count:
            break

        # 清屏
        output = ""
        if sys.stdout.isatty():
            output += clear_cmd

        # 执行扫描
        scanner = SkillsScanner(args.path)
        if args.skill:
            skill_path = Path(args.path) / args.skill
            if skill_path.exists():
                rep = scanner._scan_single_skill(skill_path)
                scanner.skills[args.skill] = rep
            else:
                print(f"❌ Skill 不存在: {args.skill}", file=sys.stderr)
                sys.exit(1)
        else:
            scanner.scan_all()

        # 根据格式输出
        fmt = args.format.lower()
        if fmt == 'json':
            result = format_json_output(scanner)
        elif fmt == 'quiet':
            result = format_quiet(scanner)
        elif fmt == 'markdown':
            result = format_markdown_output(scanner, args.output_dir or "")
        else:  # table
            result = format_table(scanner, args.verbose)

        output += result

        # watch 信息栏
        watch_info = (
            f"\n{'─' * 56}\n"
            f"  🔍 Watch mode | Interval: {interval}s | "
            f"Cycle: {count}" + (f"/{max_count}" if max_count else "") +
            " | Ctrl+C to exit\n"
        )
        output += watch_info
        print(output)

        if max_count > 0 and count >= max_count:
            break

        time.sleep(interval)


# ════════════════════════════════════════════════════════
#  主入口
# ════════════════════════════════════════════════════════

def main():
    default_skills_path = str(Path.home() / ".workbuddy" / "skills")

    parser = argparse.ArgumentParser(
        prog="health-check",
        description="Skills Health Guard — AI Agent Skills Environment Health Monitor",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""\
Examples:
  %(prog)s                       Quick scan with colored table output
  %(prog)s --format json         JSON output for piping to other tools
  %(prog)s --format quiet        Only show one-line summary
  %(prog)s --format markdown     Full markdown report with suggestions
  %(prog)s --watch 60            Re-scan every 60 seconds
  %(prog)s --watch 30 --watch-count 10   Scan 10 times, 30s apart
  %(prog)s -o report.md          Save markdown report to file
  %(prog)s --skip-fix            Skip auto-fix step
  %(prog)s -v                    Verbose output (show issues per skill)
  %(prog)s --skill prompt-engineer  Scan only a specific skill
  %(prog)s --no-color            Disable colored output""",
    )

    # ── 输出格式 ──
    parser.add_argument(
        "-f", "--format",
        choices=["json", "table", "quiet", "markdown"],
        default="table",
        help="Output format (default: table)"
    )

    # ── Watch 模式 ──
    parser.add_argument(
        "-w", "--watch",
        type=int,
        metavar="INTERVAL",
        help="Enable watch mode: re-scan every N seconds (default: 30)"
    )
    parser.add_argument(
        "--watch-count",
        type=int,
        metavar="N",
        default=0,
        help="Max number of watch cycles (default: unlimited)"
    )

    # ── 输出路径 ──
    parser.add_argument(
        "-o", "--output",
        type=str,
        metavar="PATH",
        help="Save output to file path"
    )
    parser.add_argument(
        "--output-dir",
        type=str,
        metavar="DIR",
        help="Report output directory (for markdown/html reports)"
    )

    # ── 行为控制 ──
    parser.add_argument(
        "--skip-fix",
        action="store_true",
        help="Skip the auto-fix step after scanning"
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Preview fixes without applying (for fix operations)"
    )

    # ── 详细程度 ──
    parser.add_argument(
        "-v", "--verbose",
        action="store_true",
        help="Show detailed output including per-skill issues and dependencies"
    )

    # ── 路径参数 ──
    parser.add_argument(
        "--path",
        type=str,
        default=default_skills_path,
        help=f"Skills directory path (default: {default_skills_path})"
    )
    parser.add_argument(
        "--skill",
        type=str,
        metavar="NAME",
        help="Scan only a specific skill by name"
    )

    # ── 外观控制 ──
    parser.add_argument(
        "--no-color",
        action="store_true",
        help="Disable colored terminal output"
    )

    args = parser.parse_args()

    # 如果设置了 --no-color，设置环境变量让 colorize 生效
    if args.no_color:
        os.environ['NO_COLOR'] = '1'

    # ── Watch 模式入口 ──
    if args.watch is not None:
        # 设置默认间隔
        args.watch_interval = args.watch if args.watch > 0 else 30
        run_watch_mode(args)
        return

    # ── 单次扫描模式 ──
    scanner = SkillsScanner(args.path)

    # 单个 skill 扫描
    if args.skill:
        skill_path = Path(args.path) / args.skill
        if skill_path.exists():
            report = scanner._scan_single_skill(skill_path)
            scanner.skills[args.skill] = report
        else:
            print(f"❌ Skill 不存在: {args.skill}", file=sys.stderr)
            sys.exit(1)
    else:
        scanner.scan_all()

    # 根据格式生成输出
    fmt = args.format.lower()
    if fmt == 'json':
        result = format_json_output(scanner)
    elif fmt == 'quiet':
        result = format_quiet(scanner)
    elif fmt == 'markdown':
        output_dir = args.output_dir or ""
        result = format_markdown_output(scanner, output_dir)
    elif fmt == 'table':
        result = format_table(scanner, args.verbose)
    else:
        result = format_table(scanner, args.verbose)

    # ── 输出到文件或 stdout ──
    if args.output:
        out_path = Path(args.output)
        out_path.parent.mkdir(parents=True, exist_ok=True)
        out_path.write_text(result, encoding='utf-8')
        print(f"✅ Report saved to: {out_path}", file=sys.stderr)
        # 同时也打印到 stdout（除非是 json/quiet 的纯数据模式）
        if fmt not in ('json', 'quiet'):
            print(result)
    else:
        print(result)

    # ── 可选的修复步骤 ──
    if not args.skip_fix:
        summary = scanner.get_summary()
        critical_count = summary.get('critical_count', 0)
        warning_count = summary.get('warning_count', 0)
        if critical_count > 0 or warning_count > 0:
            if not args.dry_run:
                print(
                    "\n💡 Tip: Run with --dry-run to preview fixes, "
                    "or use fixer.py directly for repairs.",
                    file=sys.stderr
                )


if __name__ == "__main__":
    main()
