#!/usr/bin/env python3
"""
Skills Environment Scanner - 技能环境依赖扫描器
扫描所有 skills 目录，提取依赖、运行时需求、环境变量要求
"""

import os
import re
import json
import subprocess
import sys
from pathlib import Path
from dataclasses import dataclass, field, asdict
from typing import Optional
from datetime import datetime

# 跨平台工具检测
from platform_utils import find_chrome_path, check_chrome_installed


@dataclass
class SkillDependency:
    """单个依赖项"""
    name: str
    version_spec: str = ""
    dep_type: str = "unknown"  # pip, npm, bun, system, api_key, env_var
    source_file: str = ""
    is_installed: Optional[bool] = None
    installed_version: Optional[str] = None
    is_optional: bool = False


@dataclass
class SkillReport:
    """单个 Skill 的扫描报告"""
    name: str
    path: str
    has_scripts: bool = False
    script_files: list = field(default_factory=list)
    dependencies: list = field(default_factory=list)
    runtime_requirements: list = field(default_factory=list)  # uv, bun, npx, node, python3.10+
    env_vars: list = field(default_factory=list)  # API keys etc.
    has_package_json: bool = False
    has_requirements_txt: bool = False
    has_pyproject_toml: bool = False
    uses_uv: bool = False
    uses_bun: bool = False
    uses_npx: bool = False
    skill_md_exists: bool = False
    health_score: int = 0  # 0-100
    issues: list = field(default_factory=list)
    warnings: list = field(default_factory=list)
    last_scanned: str = ""


class SkillsScanner:
    """Skills 环境扫描器"""

    def __init__(self, skills_base_path: str):
        self.skills_base = Path(skills_base_path)
        self.skills: dict[str, SkillReport] = {}
        self.global_issues: list[dict] = []

        # 已知的运行时工具
        self.RUNTIME_TOOLS = {
            "uv": {"check": "uv --version", "type": "system"},
            "bun": {"check": "bun --version", "type": "system"},
            "npx": {"check": "npx --version", "type": "system"},
            "node": {"check": "node --version", "type": "system"},
            "npm": {"check": "npm --version", "type": "system"},
            "pnpm": {"check": "pnpm --version", "type": "system"},
            "python3": {"check": "python3 --version", "type": "system"},
            "pip3": {"check": "pip3 --version", "type": "system"},
            "playwright": {"check": "playwright --version", "type": "pip"},
            # Chrome 检测在运行时动态处理，不在静态字典中硬编码
        }

        # Python 包版本检测模式
        self.PIP_DEP_PATTERNS = [
            # pip install xxx>=1.0
            r'(?:pip\s+install\s+)([a-zA-Z0-9_-]+)(?:\s*([><=!~]+\s*[\d.,]+))?',
            # requires-python / dependencies in inline script metadata
            r'["\']([a-zA-Z0-9_-]+)(?:[><=!~]+[\d.\s*,\s]*)?["\']',
            # import xxx
            r'^import\s+([a-zA-Z_][a-zA-Z0-9_]*)',
            r'^from\s+([a-zA-Z_][a-zA-Z0-9_]*)\s+import',
        ]

        # NPM/Node 依赖模式
        self.NPM_DEP_PATTERNS = [
            r'"([^"]+)":\s*"([^"]+)"',  # package.json format
        ]

        # API Key / 环境变量模式 — 更严格
        self.ENV_VAR_PATTERNS = [
            r'(?:export\s+)?([A-Z_][A-Z0-9_]*API[_]?[A-Z_]*(?:KEY|TOKEN|SECRET)?)',
            r"os\.environ\.get\(['\"]([^'\"]{2,30})['\"]",
            r"(?:getenv|os\.environ)\s*\(\s*[\"']([^\"']{2,30})[\"']",
            r'\$\{?([A-Z_]{3,25})\}?',
            r'(GEMINI_API_KEY|OPENAI_API_KEY|ANTHROPIC_API_KEY|FIRECRAWL_API_KEY|NOTION_TOKEN|OPENSPACE_API_KEY)',
        ]

    def scan_all(self) -> dict[str, SkillReport]:
        """扫描所有 skills"""
        if not self.skills_base.exists():
            print(f"❌ Skills 目录不存在: {self.skills_base}")
            return {}

        skill_dirs = [d for d in self.skills_base.iterdir()
                      if d.is_dir() and not d.name.startswith('.')]

        print(f"🔍 开始扫描 {len(skill_dirs)} 个 skills...\n")

        for skill_dir in sorted(skill_dirs):
            report = self._scan_single_skill(skill_dir)
            self.skills[skill_dir.name] = report

        # 全局冲突检测
        self._detect_global_conflicts()

        return self.skills

    def _scan_single_skill(self, skill_dir: Path) -> SkillReport:
        """扫描单个 skill"""
        report = SkillReport(
            name=skill_dir.name,
            path=str(skill_dir),
            last_scanned=datetime.now().isoformat(),
        )

        # 1. 检查 SKILL.md
        skill_md = skill_dir / "SKILL.md"
        if skill_md.exists():
            report.skill_md_exists = True
            self._parse_skill_md(skill_md, report)

        # 2. 扫描脚本文件
        scripts_dir = skill_dir / "scripts"
        if scripts_dir.exists():
            report.has_scripts = True
            for script_file in scripts_dir.rglob("*"):
                if script_file.is_file() and not script_file.name.startswith('.'):
                    report.script_files.append(str(script_file.relative_to(skill_dir)))
                    self._parse_script_file(script_file, report)

        # 3. 检查包管理文件
        if (skill_dir / "package.json").exists():
            report.has_package_json = True
            self._parse_package_json(skill_dir / "package.json", report)
        if (skill_dir / "requirements.txt").exists():
            report.has_requirements_txt = True
            self._parse_requirements_txt(skill_dir / "requirements.txt", report)
        if (skill_dir / "pyproject.toml").exists():
            report.has_pyproject_toml = True

        # 4. 检查根目录脚本
        for f in skill_dir.iterdir():
            if f.suffix in ('.py', '.sh', '.ts', '.js') and f.name != 'SKILL.md':
                if str(f.relative_to(skill_dir)) not in report.script_files:
                    report.script_files.append(f.name)
                    self._parse_script_file(f, report)

        # 5. 计算健康评分
        report.health_score = self._calculate_health_score(report)

        return report

    def _parse_skill_md(self, md_path: Path, report: SkillReport):
        """解析 SKILL.md 提取依赖信息"""
        content = md_path.read_text(errors='ignore')

        # 检查运行时关键词
        content_lower = content.lower()
        if 'uv run' in content_lower or '`uv`' in content:
            report.uses_uv = True
            report.runtime_requirements.append("uv")
        if 'bun' in content_lower:
            report.uses_bun = True
            report.runtime_requirements.append("bun")
        if 'npx' in content_lower or 'npx -y' in content_lower:
            report.uses_npx = True
            report.runtime_requirements.append("npx")

        # 提取 pip install 行
        for match in re.finditer(r'pip(?:install)?3?\s+(.+)', content):
            deps_str = match.group(1)
            # 清理常见的 shell 字符
            deps_str = re.sub(r'[&|$>`\\]', '', deps_str).strip()
            for part in deps_str.split():
                part = part.strip().rstrip('[],')
                if part and not part.startswith('-'):
                    ver_match = re.match(r'([a-zA-Z0-9_-]+)(.*)', part)
                    if ver_match:
                        dep = SkillDependency(
                            name=ver_match.group(1),
                            version_spec=ver_match.group(2),
                            dep_type="pip",
                            source_file="SKILL.md"
                        )
                        report.dependencies.append(dep)

        # 提取环境变量/API Key
        for pattern in self.ENV_VAR_PATTERNS:
            for match in re.finditer(pattern, content, re.IGNORECASE):
                var_name = match.group(1)
                if var_name and len(var_name) > 2 and var_name not in report.env_vars:
                    report.env_vars.append(var_name)

    def _parse_script_file(self, script_path: Path, report: SkillReport):
        """解析脚本文件提取依赖"""
        try:
            content = script_path.read_text(errors='ignore')
        except Exception:
            return

        ext = script_path.suffix.lower()

        if ext == '.py':
            self._parse_python_script(content, script_path, report)
        elif ext in ('.ts', '.js'):
            self._parse_node_script(content, script_path, report)
        elif ext == '.sh':
            self._parse_shell_script(content, script_path, report)

    def _parse_python_script(self, content: str, script_path: Path, report: SkillReport):
        """解析 Python 脚本"""
        rel_path = script_path.name

        # PEP 723 inline script metadata (/// script dependencies)
        script_meta = re.findall(
            r'#\s*dependencies\s*=\s*\[(.*?)\]',
            content, re.DOTALL
        )
        for meta_block in script_meta:
            # 解析 ["pkg>=1.0", "pkg2"]
            deps = re.findall(r'["\']([a-zA-Z0-9_-]+)(?:\s*([><=!~]+[\d.\s*,\s]*))?["\']', meta_block)
            for name, ver in deps:
                dep = SkillDependency(
                    name=name,
                    version_spec=ver.strip() if ver else "",
                    dep_type="pip",
                    source_file=rel_path,
                )
                # 去重
                existing_names = [d.name for d in report.dependencies]
                if name not in existing_names:
                    report.dependencies.append(dep)

        # import 语句
        for pattern in [r'^import\s+([a-zA-Z_][\w.]*)', r'^from\s+([a-zA-Z_][\w.]*)\s+import']:
            for match in re.finditer(pattern, content, re.MULTILINE):
                mod_name = match.group(1).split('.')[0]
                # 过滤标准库
                stdlib = {'os', 'sys', 're', 'json', 'pathlib', 'datetime', 'dataclass',
                         'typing', 'argparse', 'subprocess', 'collections', 'itertools',
                         'functools', 'hashlib', 'base64', 'uuid', 'textwrap', 'copy',
                         'io', 'abc', 'contextlib', 'enum', 'logging', 'warnings',
                         'time', 'date', 'calendar', 'math', 'random', 'operator'}
                if mod_name not in stdlib and mod_name not in [d.name for d in report.dependencies]:
                    dep = SkillDependency(name=mod_name, dep_type="pip", source_file=rel_path)
                    report.dependencies.append(dep)

        # 环境变量
        for match in re.finditer(r"os\.environ\.get\(['\"]([^'\"]+)['\"]", content):
            var = match.group(1)
            if var not in report.env_vars:
                report.env_vars.append(var)

        # uv run 检测
        if 'uv run' in content[:200]:  # 通常在前几行
            report.uses_uv = True
            if "uv" not in report.runtime_requirements:
                report.runtime_requirements.append("uv")

    def _parse_node_script(self, content: str, script_path: Path, report: SkillReport):
        """解析 TypeScript/JavaScript 脚本"""
        rel_path = script_path.name

        # require / import
        for match in re.finditer(r'(?:require|import)\s*\(?["\'](@?[a-zA-Z0-9_/~-]+)["\']', content):
            mod_name = match.group(1)
            # 过滤相对路径和 Node 内置
            if not mod_name.startswith('.') and mod_name not in [d.name for d in report.dependencies]:
                dep = SkillDependency(name=mod_name, dep_type="npm", source_file=rel_path)
                report.dependencies.append(dep)

        # bun 检测
        if 'bun' in content[:200]:
            report.uses_bun = True
            if "bun" not in report.runtime_requirements:
                report.runtime_requirements.append("bun")

    def _parse_shell_script(self, content: str, script_path: Path, report: SkillReport):
        """解析 Shell 脚本"""
        rel_path = script_path.name

        # pip install / npm install
        for match in re.finditer(r'(pip3?\s+install|npm\s+install)\s+(.+)', content):
            deps_str = match.group(2)
            for part in re.split(r'[\s\n]', deps_str):
                part = re.sub(r'[^a-zA-Z0-9_.-><==~].*', '', part).strip()
                if len(part) > 1 and part not in ['--user', '-g', '--save', '-dev']:
                    dep_type = "pip" if 'pip' in match.group(1) else "npm"
                    if part not in [d.name for d in report.dependencies]:
                        dep = SkillDependency(name=part, dep_type=dep_type, source_file=rel_path)
                        report.dependencies.append(dep)

        # 运行时命令
        for cmd in ['uv ', 'bun ', 'npx ', 'node ', 'playwright ']:
            if cmd in content and cmd.strip() not in report.runtime_requirements:
                report.runtime_requirements.append(cmd.strip())

    def _parse_package_json(self, pkg_path: Path, report: SkillReport):
        """解析 package.json"""
        try:
            data = json.loads(pkg_path.read_text())
            deps = {}
            deps.update(data.get('dependencies', {}))
            deps.update(data.get('devDependencies', {}))
            for name, version in deps.items():
                if name not in [d.name for d in report.dependencies]:
                    dep = SkillDependency(
                        name=name, version_spec=str(version), dep_type="npm",
                        source_file="package.json"
                    )
                    report.dependencies.append(dep)
        except Exception as e:
            report.warnings.append(f"无法解析 package.json: {e}")

    def _parse_requirements_txt(self, req_path: Path, report: SkillReport):
        """解析 requirements.txt"""
        try:
            for line in req_path.read_text().splitlines():
                line = line.strip()
                if line and not line.startswith('#'):
                    parts = re.split(r'[><=~!]+', line, maxsplit=1)
                    name = parts[0].strip()
                    ver = parts[1] if len(parts) > 1 else ""
                    if name and name not in [d.name for d in report.dependencies]:
                        dep = SkillDependency(name=name, version_spec=ver, dep_type="pip",
                                            source_file="requirements.txt")
                        report.dependencies.append(dep)
        except Exception as e:
            report.warnings.append(f"无法解析 requirements.txt: {e}")

    def _calculate_health_score(self, report: SkillReport) -> int:
        """计算健康评分 (0-100)"""
        score = 100

        # 无 SKILL.md 扣分
        if not report.skill_md_exists:
            score -= 15
            report.issues.append("缺少 SKILL.md 文件")

        # 有脚本但无任何依赖声明
        if report.has_scripts and not report.dependencies:
            score -= 5
            report.warnings.append("有脚本但未发现明确依赖声明")

        # 检查运行时可用性
        missing_runtime = []
        for runtime in report.runtime_requirements:
            is_avail = self._check_tool_available(runtime)
            if not is_avail:
                missing_runtime.append(runtime)
                score -= 15
                report.issues.append(f"缺少运行时: {runtime}")

        # 检查 API Key 环境变量
        missing_keys = []
        for env_var in report.env_vars:
            if not os.environ.get(env_var):
                missing_keys.append(env_var)
        if missing_keys:
            score -= min(len(missing_keys) * 5, 20)
            report.warnings.append(f"未设置环境变量: {', '.join(missing_keys)}")

        # 有 Python 脚本的检查
        py_scripts = [f for f in report.script_files if f.endswith('.py')]
        if py_scripts and not self._check_tool_available('python3'):
            score -= 20
            report.issues.append("Python 脚本但系统无 python3")

        return max(0, min(100, score))

    def _check_tool_available(self, tool: str) -> bool:
        """检查工具是否可用"""
        try:
            if tool == 'chrome':
                # 跨平台 Chrome 检测
                return check_chrome_installed()
            elif tool == 'playwright':
                # 特殊处理：playwright 可能是 Python 包
                result = subprocess.run(
                    ["python3", "-m", "playwright", "--version"],
                    capture_output=True, timeout=10
                )
                return result.returncode == 0
            else:
                result = subprocess.run(
                    [tool, "--version"],
                    capture_output=True, timeout=5
                )
                return result.returncode == 0
        except (FileNotFoundError, subprocess.TimeoutExpired, OSError):
            return False

    def _detect_global_conflicts(self):
        """检测全局冲突"""
        # 收集所有依赖
        all_deps: dict[str, list] = {}  # dep_name -> [(skill_name, version_spec)]
        for skill_name, report in self.skills.items():
            for dep in report.dependencies:
                if dep.name not in all_deps:
                    all_deps[dep.name] = []
                all_deps[dep.name].append((skill_name, dep.version_spec, dep.dep_type))

        # 版本冲突检测
        for dep_name, usages in all_deps.items():
            if len(usages) > 1:
                versions = set()
                for _, ver_spec, _ in usages:
                    if ver_spec:
                        versions.add(ver_spec)
                if len(versions) > 1:
                    self.global_issues.append({
                        "type": "version_conflict",
                        "dependency": dep_name,
                        "usages": [{"skill": s, "version": v, "type": t} for s, v, t in usages],
                        "severity": "warning"
                    })

        # 运行时冲突检测（如同时需要不同版本的 node）
        runtime_usage: dict[str, list] = {}
        for skill_name, report in self.skills.items():
            for rt in report.runtime_requirements:
                if rt not in runtime_usage:
                    runtime_usage[rt] = []
                runtime_usage[rt].append(skill_name)

        for rt, skills_using in runtime_usage.items():
            if len(skills_using) > 3:  # 超过3个 skill 使用同一运行时
                self.global_issues.append({
                    "type": "heavy_runtime_dependency",
                    "runtime": rt,
                    "used_by": skills_using,
                    "count": len(skills_using),
                    "severity": "info"
                })

    def get_summary(self) -> dict:
        """获取总体摘要"""
        total = len(self.skills)
        if total == 0:
            return {"total": 0}

        scores = [r.health_score for r in self.skills.values()]
        avg_score = sum(scores) / total
        healthy = sum(1 for s in scores if s >= 80)
        warning = sum(1 for s in scores if 50 <= s < 80)
        critical = sum(1 for s in scores if s < 50)

        with_scripts = sum(1 for r in self.skills.values() if r.has_scripts)
        with_deps = sum(1 for r in self.skills.values() if r.dependencies)

        all_runtimes = set()
        all_env_vars = set()
        total_deps = 0
        for r in self.skills.values():
            all_runtimes.update(r.runtime_requirements)
            all_env_vars.update(r.env_vars)
            total_deps += len(r.dependencies)

        return {
            "total_skills": total,
            "avg_health_score": round(avg_score, 1),
            "healthy_count": healthy,
            "warning_count": warning,
            "critical_count": critical,
            "skills_with_scripts": with_scripts,
            "skills_with_dependencies": with_deps,
            "total_dependencies": total_deps,
            "unique_runtimes": sorted(all_runtimes),
            "unique_env_vars": sorted(all_env_vars),
            "global_issues": self.global_issues,
            "scan_time": datetime.now().isoformat(),
        }

    def to_json(self, filepath: Optional[str] = None) -> str:
        """导出 JSON 报告"""
        data = {
            "summary": self.get_summary(),
            "skills": {name: asdict(report) for name, report in self.skills.items()}
        }
        json_str = json.dumps(data, ensure_ascii=False, indent=2)
        if filepath:
            Path(filepath).write_text(json_str, encoding='utf-8')
        return json_str


# ════════════════════════════════════════════════════════
#  Python 版本检查
# ════════════════════════════════════════════════════════
MIN_PYTHON_VERSION = (3, 12)

def check_python_version():
    """检查 Python 版本是否符合要求"""
    if sys.version_info < MIN_PYTHON_VERSION:
        print(f"\n{'='*60}")
        print(f"  ❌ 错误: Python 版本不足")
        print(f"{'='*60}")
        print(f"\n  Skills Health Guardian 需要 Python {MIN_PYTHON_VERSION[0]}.{MIN_PYTHON_VERSION[1]} 或更高版本")
        print(f"  当前版本: Python {sys.version}")
        print(f"\n  💡 如何升级 Python:")
        print(f"     • macOS:    brew install python@3.12")
        print(f"     • Linux:    sudo apt install python3.12")
        print(f"     • Windows:  https://www.python.org/downloads/")
        print(f"\n{'='*60}\n")
        sys.exit(1)

def main():
    # 首先检查 Python 版本
    check_python_version()

    # 默认路径
    default_path = Path.home() / ".workbuddy" / "skills"

    import argparse
    parser = argparse.ArgumentParser(description="Skills Environment Scanner")
    parser.add_argument("--path", type=str, default=str(default_path), help="Skills 目录路径")
    parser.add_argument("--output", "-o", type=str, help="输出 JSON 文件路径")
    parser.add_argument("--json", action="store_true", help="仅输出 JSON 格式")
    parser.add_argument("--skill", type=str, help="仅扫描指定 skill")
    args = parser.parse_args()

    scanner = SkillsScanner(args.path)

    if args.skill:
        skill_path = Path(args.path) / args.skill
        if skill_path.exists():
            report = scanner._scan_single_skill(skill_path)
            scanner.skills[args.skill] = report
        else:
            print(f"❌ Skill 不存在: {args.skill}")
            sys.exit(1)
    else:
        scanner.scan_all()

    if args.json or args.output:
        output = scanner.to_json(args.output)
        if args.json and not args.output:
            print(output)
    else:
        # 友好的终端输出
        print_report(scanner)


def print_report(scanner: SkillsScanner):
    """打印友好的终端报告"""
    summary = scanner.get_summary()
    sep = "─" * 60

    print("\n" + "=" * 60)
    print("  🏥 Skills 环境健康报告")
    print("=" * 60)
    print(f"  📊 扫描时间: {summary['scan_time'][:19]}")
    print(f"  📦 Skill 总数: {summary['total_skills']}")

    # 健康分数条
    avg = summary['avg_health_score']
    bar_len = 30
    filled = int(bar_len * avg / 100)
    bar = "█" * filled + "░" * (bar_len - filled)
    color = "\033[32m" if avg >= 80 else "\033[33m" if avg >= 50 else "\033[31m"
    reset = "\033[0m"
    print(f"\n  🌡️  全局健康指数: {color}{avg:.1f}/100{reset}  [{bar}]")

    print(f"\n  ✅ 健康 (≥80): {summary['healthy_count']}")
    print(f"  ⚠️  警告 (50-79): {summary['warning_count']}")
    print(f"  🔴 异常 (<50): {summary['critical_count']}")

    print("\n  📋 依赖统计:")
    print(f"     有脚本的 Skills: {summary['skills_with_scripts']}")
    print(f"     有依赖声明的:     {summary['skills_with_dependencies']}")
    print(f"     总依赖项数:       {summary['total_dependencies']}")

    if summary['unique_runtimes']:
        print(f"\n  🔧 运行时需求: {', '.join(summary['unique_runtimes'])}")
    if summary['unique_env_vars']:
        print(f"  🔑 环境变量需求: {', '.join(summary['unique_env_vars'][:10])}")
        if len(summary['unique_env_vars']) > 10:
            print(f"     ... 还有 {len(summary['unique_env_vars']) - 10} 个")

    # 全局问题
    if summary['global_issues']:
        print(f"\n  ⚡ 全局冲突/警告 ({len(summary['global_issues'])}):")
        for issue in summary['global_issues']:
            sev = "🔴" if issue.get('severity') == 'warning' else "ℹ️ "
            if issue['type'] == 'version_conflict':
                print(f"     {sev} 依赖版本冲突: {issue['dependency']}")
                for u in issue['usages']:
                    print(f"        - {u['skill']}: 要求 {u['version'] or '(任意)'} ({u['type']})")
            elif issue['type'] == 'heavy_runtime_dependency':
                print(f"     {sev} 高频运行时: {issue['runtime']} 被 {issue['count']} 个 skill 使用")

    # 每个 skill 详情
    print(f"\n{sep}")
    print("  📝 各 Skill 详情:\n")

    sorted_skills = sorted(scanner.skills.items(), key=lambda x: x[1].health_score)
    for name, report in sorted_skills:
        score_color = "\033[32m" if report.health_score >= 80 else "\033[33m" if report.health_score >= 50 else "\033[31m"
        icon = "✅" if report.health_score >= 80 else "⚠️" if report.health_score >= 50 else "🔴"

        deps_short = []
        for d in report.dependencies[:5]:
            deps_short.append(d.name + (d.version_spec if d.version_spec else ""))
        deps_str = ", ".join(deps_short)
        if len(report.dependencies) > 5:
            deps_str += f" (+{len(report.dependencies)-5})"

        runtime_str = ", ".join(report.runtime_requirements) if report.runtime_requirements else "-"

        print(f"  {icon} {score_color}{name}{reset} (健康:{report.health_score})")
        if report.dependencies:
            print(f"      依赖: {deps_str}")
        if report.runtime_requirements:
            print(f"      运行时: {runtime_str}")
        if report.issues:
            for issue in report.issues[:2]:
                print(f"      ❌ {issue}")
        if report.warnings:
            for warn in report.warnings[:2]:
                print(f"      ⚠️  {warn}")
        print()

    print(sep)
    print("  💡 提示: 使用 --json 参数导出机器可读报告，或 --output report.json 保存")
    print()


if __name__ == "__main__":
    main()
