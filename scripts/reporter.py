#!/usr/bin/env python3
"""
Skills Health Reporter - 健康状态报告生成器
生成 Markdown/JSON 格式的环境健康报告，支持定期输出和趋势追踪
"""

import json
import os
from pathlib import Path
from datetime import datetime, timedelta
from dataclasses import dataclass
from typing import Optional


@dataclass
class ReportConfig:
    """报告配置"""
    output_dir: str = ""
    format: str = "markdown"  # markdown, json, html
    include_trend: bool = True
    max_history: int = 30  # 保留最近 N 天的历史记录


class HealthReporter:
    """健康报告生成器"""

    def __init__(self, output_base: str = ""):
        self.output_base = Path(output_base) if output_base else Path.home() / ".workbuddy" / "skills" / "skills-health-guardian" / "reports"
        self.history_dir = self.output_base / "history"
        self.history_dir.mkdir(parents=True, exist_ok=True)
        self.max_history = 30  # 默认保留最近30天

    def generate(self, scan_data: dict, config: Optional[ReportConfig] = None) -> str:
        """生成完整报告"""
        cfg = config or ReportConfig()
        summary = scan_data.get("summary", {})
        skills = scan_data.get("skills", {})

        if cfg.format == "json":
            return self._generate_json(scan_data)
        elif cfg.format == "html":
            return self._generate_html(summary, skills)

        return self._generate_markdown(summary, skills, cfg.include_trend)

    def _generate_markdown(self, summary: dict, skills: dict, with_trend: bool = True) -> str:
        """生成 Markdown 报告"""
        lines = []
        lines.append("# 🏥 Skills 环境健康报告\n")
        lines.append(f"> **生成时间**: {summary.get('scan_time', '')[:19]}  |  **Skill 总数**: {summary['total_skills']}\n")

        # === 概览仪表盘 ===
        lines.append("---\n## 📊 健康概览\n")
        avg = summary.get('avg_health_score', 0)
        status_icon = "🟢" if avg >= 80 else "🟡" if avg >= 50 else "🔴"
        status_text = "良好" if avg >= 80 else "需关注" if avg >= 50 else "紧急"

        lines.append(f"| 指标 | 数值 | 状态 |")
        lines.append(f"|------|------|------|")
        lines.append(f"| 全局健康指数 | **{avg:.1f}/100** | {status_icon} {status_text} |")
        lines.append(f"| ✅ 健康 Skills (≥80) | **{summary.get('healthy_count', 0)}** | 🟢 |")
        lines.append(f"| ⚠️ 警告 Skills (50-79) | **{summary.get('warning_count', 0)}** | 🟡 |")
        lines.append(f"| 🔴 异常 Skills (<50) | **{summary.get('critical_count', 0)}** | 🔴 |")
        lines.append(f"| 有脚本依赖的 Skills | {summary.get('skills_with_scripts', 0)} | - |")
        lines.append(f"| 总依赖项数 | {summary.get('total_dependencies', 0)} | - |\n")

        # === 运行时矩阵 ===
        runtimes = summary.get('unique_runtimes', [])
        if runtimes:
            lines.append("## 🔧 运行时需求矩阵\n")
            lines.append("| 运行时工具 | 状态 | 使用该运行时的 Skills |")
            lines.append("|----------|------|---------------------|")

            for rt in sorted(runtimes):
                users = [name for name, report in skills.items() if rt in report.get('runtime_requirements', [])]
                available = self._check_rt_available(rt)
                avail_str = "✅ 已安装" if available else "❌ 未安装"
                lines.append(f"| `{rt}` | {avail_str} | {', '.join(users[:5])}{f' (+{len(users)-5})' if len(users)>5 else ''} |")
            lines.append("")

        # === 环境变量清单 ===
        env_vars = summary.get('unique_env_vars', [])
        if env_vars:
            lines.append("## 🔑 API Key / 环境变量清单\n")
            lines.append("| 变量名 | 状态 | 相关 Skills |")
            lines.append("|--------|------|-----------|")
            for var in env_vars:
                is_set = bool(os.environ.get(var))
                set_str = "✅ 已配置" if is_set else "⚠️ 未配置"
                related = [name for name, report in skills.items() if var in report.get('env_vars', [])]
                lines.append(f"`{var}` | {set_str} | {', '.join(related[:3])}{'' if len(related)<=3 else f' (+{len(related)-3})'} |")
            lines.append("")

        # === 全局冲突 ===
        issues = summary.get('global_issues', [])
        if issues:
            lines.append("## ⚡ 全局冲突与警告\n")
            for issue in issues:
                sev = "🔴 **警告**" if issue.get('severity') == 'warning' else "ℹ️ **信息**"
                if issue['type'] == 'version_conflict':
                    lines.append(f"- {sev} 依赖版本冲突: **{issue['dependency']}**")
                    for u in issue['usages']:
                        ver_str = f" 要求 `{u['version']}`" if u['version'] else ""
                        lines.append(f"  - `{u['skill']}`:{ver_str} ({u['type']})")
                elif issue['type'] == 'heavy_runtime_dependency':
                    lines.append(f"- {sev} 高频运行时依赖: **{issue['runtime']}** 被 {issue['count']} 个 skill 使用")
            lines.append("")

        # === 各 Skill 详情表 ===
        lines.append("## 📋 各 Skill 健康详情\n")
        sorted_skills = sorted(skills.items(), key=lambda x: x[1].get('health_score', 0))

        lines.append("| Skill | 健康分 | 依赖数 | 运行时 | 主要问题 |")
        lines.append("|-------|--------|--------|--------|---------|")

        for name, report in sorted_skills:
            score = report.get('health_score', 0)
            score_badge = f"🟢 {score}" if score >= 80 else f"🟡 {score}" if score >= 50 else f"🔴 {score}"
            deps = len(report.get('dependencies', []))
            rt = ", ".join(report.get('runtime_requirements', [])) or "-"
            issues_list = report.get('issues', []) + report.get('warnings', [])
            issues_str = issues_list[0] if issues_list else "-"

            lines.append(f"| `{name}` | {score_badge} | {deps} | {rt} | {issues_str[:40]} |")
        lines.append("")

        # === 修复建议 ===
        lines.append("## 🛠️ 修复建议\n")
        suggestions = self._generate_suggestions(summary, skills)
        for sug in suggestions:
            lines.append(f"- {sug}")
        lines.append("")

        # === 趋势（如果有历史数据）===
        if with_trend:
            trend = self._load_trend()
            if len(trend) > 1:
                lines.append("## 📈 健康趋势 (最近 7 次)\n")
                lines.append("| 日期 | 平均分 | 健康 | 警告 | 异常 |")
                lines.append("|------|--------|------|------|------|")
                for t in trend[-7:]:
                    lines.append(f"| {t['time'][:10]} | {t['avg']:.1f} | {t['healthy']} | {t['warning']} | {t['critical']} |")
                lines.append("")

        report_text = "\n".join(lines)

        # 保存本次快照
        self._save_snapshot(summary)

        return report_text

    def _generate_json(self, scan_data: dict) -> str:
        """生成 JSON 报告"""
        return json.dumps(scan_data, ensure_ascii=False, indent=2)

    def _generate_html(self, summary: dict, skills: dict) -> str:
        """生成 HTML 报告（简化版）"""
        avg = summary.get('avg_health_score', 0)
        color = "#22c55e" if avg >= 80 else "#eab308" if avg >= 50 else "#ef4444"

        html = f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Skills 环境健康报告</title>
<style>
* {{ margin: 0; padding: 0; box-sizing: border-box; }}
body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
       background: #0a0a0a; color: #e4e4e7; padding: 2rem; }}
.container {{ max-width: 1100px; margin: 0 auto; }}
h1 {{ font-size: 2rem; font-weight: 700; margin-bottom: 0.5rem; color: #fff; }}
.subtitle {{ color: #71717a; margin-bottom: 2rem; }}
.dashboard {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
             gap: 1rem; margin-bottom: 2rem; }}
.card {{ background: rgba(255,255,255,0.05); border: 1px solid rgba(255,255,255,0.08);
         border-radius: 16px; padding: 1.5rem; backdrop-filter: blur(10px); }}
.score-card {{ grid-column: span 2; text-align: center; }}
.score-big {{ font-size: 4rem; font-weight: 800; color: {color}; line-height: 1; }}
.score-label {{ color: #a1a1aa; font-size: 0.9rem; margin-top: 0.25rem; }}
.stat-num {{ font-size: 2rem; font-weight: 700; color: #fff; }}
.stat-label {{ color: #71717a; font-size: 0.85rem; margin-top: 0.25rem; }}
table {{ width: 100%; border-collapse: collapse; margin-top: 1rem; }}
th {{ text-align: left; padding: 0.75rem 1rem; background: rgba(255,255,255,0.05);
     color: #a1a1aa; font-size: 0.8rem; text-transform: uppercase; letter-spacing: 0.05em;
     position: sticky; top: 0; }}
td {{ padding: 0.75rem 1rem; border-bottom: 1px solid rgba(255,255,255,0.05); font-size: 0.9rem; }}
tr:hover td {{ background: rgba(255,255,255,0.03); }}
.section-title {{ font-size: 1.25rem; font-weight: 600; margin: 2rem 0 1rem; color: #fff; }}
.tag {{ display: inline-block; padding: 2px 8px; border-radius: 6px; font-size: 0.75rem;
       font-weight: 500; background: rgba(255,255,255,0.08); }}
.tag-ok {{ background: rgba(34,197,94,0.15); color: #22c55e; }}
.tag-warn {{ background: rgba(234,179,8,0.15); color: #eab308; }}
.tag-bad {{ background: rgba(239,68,68,0.15); color: #ef4444; }}
</style>
</head>
<body>
<div class="container">
<h1>🏥 Skills 环境健康报告</h1>
<p class="subtitle">生成时间: {summary.get('scan_time', '')[:19]}</p>

<div class="dashboard">
<div class="card score-card">
  <div class="score-big">{avg:.0f}</div>
  <div class="score-label">全局健康指数 / 100</div>
</div>
<div class="card"><div class="stat-num">{summary.get('healthy_count', 0)}</div><div class="stat-label">✅ 健康 (≥80)</div></div>
<div class="card"><div class="stat-num">{summary.get('warning_count', 0)}</div><div class="stat-label">⚠️ 警告 (50-79)</div></div>
<div class="card"><div class="stat-num">{summary.get('critical_count', 0)}</div><div class="stat-label">🔴 异常 (<50)</div></div>
</div>

<h2 class="section-title">📋 各 Skill 详情</h2>
<table>
<tr><th>Skill 名称</th><th>健康分</th><th>依赖数</th><th>运行时</th><th>问题</th></tr>
"""

        for name, report in sorted(skills.items(), key=lambda x: x[1].get('health_score', 0), reverse=True):
            score = report.get('health_score', 0)
            if score >= 80:
                tag_cls = "tag-ok"
            elif score >= 50:
                tag_cls = "tag-warn"
            else:
                tag_cls = "tag-bad"

            deps = len(report.get('dependencies', []))
            rt = ", ".join(report.get('runtime_requirements', [])) or "-"
            issues = (report.get('issues', []) or report.get('warnings', []))
            issue_str = issues[0] if issues else "-"

            html += f'<tr><td><code>{name}</code></td>'
            html += f'<td><span class="tag {tag_cls}">{score}</span></td>'
            html += f'<td>{deps}</td><td><code>{rt}</code></td>'
            html += f'<td>{issue_str[:50]}</td></tr>\n'

        html += "</table></div></body></html>"
        return html

    def _check_rt_available(self, rt: str) -> bool:
        """快速检查运行时是否可用"""
        import subprocess
        try:
            if rt == 'chrome':
                r = subprocess.run(["/Applications/Google Chrome.app/Contents/MacOS/Google Chrome", "--version"],
                                 capture_output=True, timeout=5)
                return r.returncode == 0
            elif rt == 'playwright':
                r = subprocess.run(["python3", "-m", "playwright", "--version"],
                                 capture_output=True, timeout=10)
                return r.returncode == 0
            r = subprocess.run([rt, "--version"], capture_output=True, timeout=5,
                             stderr=subprocess.DEVNULL, stdout=subprocess.DEVNULL)
            return r.returncode == 0
        except Exception:
            return False

    def _generate_suggestions(self, summary: dict, skills: dict) -> list:
        """生成智能修复建议"""
        suggestions = []

        # 运行时缺失建议
        for rt in summary.get('unique_runtimes', []):
            if not self._check_rt_available(rt):
                install_cmds = {
                    "uv": "curl -LsSf https://astral.sh/uv/install.sh | sh",
                    "bun": "curl -fsSL https://bun.sh/install | bash",
                    "npx": "安装 Node.js: brew install node",
                    "pnpm": "npm install -g pnpm",
                    "playwright": "pip3 install playwright && playwright install chromium",
                    "chrome": "已预装 macOS 或从 google.com/chrome 下载",
                }
                cmd = install_cmds.get(rt, f"# 安装 {rt}")
                suggestions.append(f"**缺少 `{rt}`**: `{cmd}`")

        # 环境变量未设置
        for var in summary.get('unique_env_vars', []):
            if not os.environ.get(var):
                suggestions.append(f"**环境变量 ` {var}` 未设置** — 在 ~/.zshrc 中 export 该变量，或使用 WorkBuddy 连接云服务获取密钥")

        # 低分 skill 建议
        for name, report in sorted(skills.items(), key=lambda x: x[1].get('health_score', 0)):
            if report.get('health_score', 100) < 60 and report.get('issues'):
                for issue in report.get('issues', [])[:1]:
                    suggestions.append(f"**`{name}`**: {issue}")

        # 隔离建议
        dep_counts: dict[str, int] = {}
        for name, report in skills.items():
            for d in report.get('dependencies', []):
                dep_name = d.get('name', '')
                dep_type = d.get('dep_type', '')
                if dep_type == 'pip':
                    dep_counts[dep_name] = dep_counts.get(dep_name, 0) + 1

        conflicts = [k for k, v in dep_counts.items() if v >= 3]
        if conflicts:
            suggestions.append(f"**依赖共享风险**: `{', '.join(conflicts[:5])}` 被 3+ 个 skill 共享，建议考虑使用虚拟环境隔离")

        if not suggestions:
            suggestions.append("✅ 当前环境状态良好，无需立即操作。")

        return suggestions

    def _save_snapshot(self, summary: dict):
        """保存历史快照用于趋势分析"""
        snapshot = {
            "time": summary.get('scan_time', ''),
            "avg": summary.get('avg_health_score', 0),
            "healthy": summary.get('healthy_count', 0),
            "warning": summary.get('warning_count', 0),
            "critical": summary.get('critical_count', 0),
            "total": summary.get('total_skills', 0),
        }
        date_str = summary.get('scan_time', datetime.now().isoformat())[:10]
        snap_path = self.history_dir / f"{date_str}.json"
        snapshots = []
        if snap_path.exists():
            try:
                snapshots = json.loads(snap_path.read_text())
            except Exception:
                pass
        snapshots.append(snapshot)

        # 只保留最近 30 天
        cutoff = (datetime.now() - timedelta(days=self.max_history)).isoformat()
        snapshots = [s for s in snapshots if s.get('time', '') >= cutoff]

        snap_path.write_text(json.dumps(snapshots, ensure_ascii=False, indent=2))

    def _load_trend(self) -> list:
        """加载历史趋势"""
        all_data = []
        for snap_file in sorted(self.history_dir.glob("*.json")):
            try:
                data = json.loads(snap_file.read_text())
                all_data.extend(data)
            except Exception:
                continue
        all_data.sort(key=lambda x: x.get('time', ''))
        return all_data[-30:]  # 最近 30 条

    def save_report(self, content: str, filename: Optional[str] = None) -> str:
        """保存报告文件"""
        self.output_base.mkdir(parents=True, exist_ok=True)
        if not filename:
            dt = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
            filename = f"health-report-{dt}.md"
        filepath = self.output_base / filename
        filepath.write_text(content, encoding='utf-8')
        return str(filepath)


def main():
    import argparse
    from scanner import SkillsScanner

    parser = argparse.ArgumentParser(description="Skills Health Reporter")
    parser.add_argument("--path", type=str, default=str(Path.home() / ".workbuddy" / "skills"))
    parser.add_argument("--output-dir", type=str, help="报告输出目录")
    parser.add_argument("-f", "--format", choices=["markdown", "json", "html"], default="markdown")
    parser.add_argument("-o", "--output-file", type=str, help="输出文件名")
    parser.add_argument("--no-trend", action="store_true", help="不包含趋势图")
    args = parser.parse_args()

    # 先扫描
    scanner = SkillsScanner(args.path)
    scanner.scan_all()
    scan_data = {
        "summary": scanner.get_summary(),
        "skills": {n: r.__dict__ if hasattr(r, '__dict__') else r for n, r in scanner.skills.items()}
    }

    # 生成报告
    reporter = HealthReporter(args.output_dir)
    config = ReportConfig(format=args.format, include_trend=not args.no_trend)
    report = reporter.generate(scan_data, config)

    # 输出
    outpath = reporter.save_report(report, args.output_file)
    print(f"\n✅ 报告已生成: {outpath}")

    if args.format != "json":
        print(report)


if __name__ == "__main__":
    main()
