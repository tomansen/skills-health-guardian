#!/usr/bin/env python3
"""
Skills Fix Engine - 自动修复与建议引擎
提供依赖安装、环境隔离建议、更新检查等功能
"""

import json
import subprocess
import os
from pathlib import Path
from datetime import datetime
from typing import Optional


class SkillsFixEngine:
    """Skills 环境修复引擎"""

    def __init__(self, skills_base_path: str):
        self.skills_base = Path(skills_base_path)
        self.fix_log: list[dict] = []

    # ================================================================
    #  公开接口
    # ================================================================

    def check_all(self) -> dict:
        """全面检查所有可修复项"""
        results = {
            "missing_runtimes": [],
            "missing_deps": {},
            "missing_env_vars": [],
            "version_conflicts": [],
            "isolation_recommendations": [],
            "update_available": [],
        }

        # 检查运行时
        runtimes_to_check = ["uv", "bun", "npx", "node", "npm", "pnpm", "python3", "pip3"]
        for rt in runtimes_to_check:
            if not self._tool_exists(rt):
                install_cmd = self._get_install_cmd(rt)
                if install_cmd:
                    results["missing_runtimes"].append({
                        "name": rt,
                        "install_cmd": install_cmd,
                        "priority": "high" if rt in ["uv", "python3"] else "medium"
                    })

        # 扫描各 skill 的缺失依赖（简化版）
        if self.skills_base.exists():
            for skill_dir in self.skills_base.iterdir():
                if not skill_dir.is_dir() or skill_dir.name.startswith('.'):
                    continue

                # 检查 requirements.txt / package.json
                req_txt = skill_dir / "requirements.txt"
                pkg_json = skill_dir / "package.json"

                missing_pip = []
                if req_txt.exists():
                    for line in req_txt.read_text().splitlines():
                        line = line.strip()
                        if line and not line.startswith('#'):
                            pkg_name = line.split('>=')[0].split('==')[0].split('<=')[0].split('~=')
                            if isinstance(pkg_name, list):
                                pkg_name = pkg_name[0]
                            pkg_name = str(pkg_name).strip().split(',')[0].strip()
                            if pkg_name and not self._pip_installed(pkg_name):
                                missing_pip.append(line)

                if missing_pip:
                    results["missing_deps"][skill_dir.name] = {
                        "type": "pip",
                        "packages": missing_pip,
                        "fix_cmd": f"cd {skill_dir} && pip3 install -r requirements.txt",
                        "auto_fixable": True
                    }

                # 检查 node_modules
                if pkg_json.exists() and not (skill_dir / "node_modules").exists():
                    try:
                        data = json.loads(pkg_json.read_text())
                        deps = list(data.get("dependencies", {}).keys())[:5]
                        if skill_dir.name not in results["missing_deps"]:
                            results["missing_deps"][skill_dir.name] = {}
                        results["missing_deps"][skill_dir.name]["node"] = {
                            "type": "npm",
                            "sample_packages": deps,
                            "fix_cmd": f"cd {skill_dir} && npm install",
                            "auto_fixable": True
                        }
                    except Exception:
                        pass

        return results

    def auto_fix(self, fix_type: str, target: str = "", dry_run: bool = True) -> dict:
        """执行自动修复
        
        Args:
            fix_type: runtime | deps | env_template | isolate
            target: 具体目标 (如 'uv', 或 skill 名称)
            dry_run: 仅预览不执行
        """
        result = {"success": False, "action": f"{fix_type}:{target}", "message": ""}

        if fix_type == "runtime":
            result = self._fix_runtime(target, dry_run)
        elif fix_type == "deps":
            result = self._fix_deps(target, dry_run)
        elif fix_type == "env_template":
            result = self._generate_env_template(dry_run)
        elif fix_type == "isolate":
            result = self._suggest_isolation(target)
        else:
            result["message"] = f"未知修复类型: {fix_type}"

        self.fix_log.append({
            "time": datetime.now().isoformat(),
            "action": f"{fix_type}:{target}",
            "dry_run": dry_run,
            **result
        })

        return result

    def generate_env_template(self, output_path: str = "") -> str:
        """生成 .env.template 文件，列出所有需要的环境变量"""
        all_vars: dict[str, list] = {}

        if self.skills_base.exists():
            for skill_dir in self.skills_base.iterdir():
                if not skill_dir.is_dir():
                    continue
                skill_md = skill_dir / "SKILL.md"
                if skill_md.exists():
                    content = skill_md.read_text(errors='ignore')
                    import re
                    patterns = [
                        r'([A-Z_][A-Z0-9_]*API[_]?[A-Z_]*(?:KEY|TOKEN|SECRET)?)',
                        r"os\.environ\.get\(['\"]([^'\"]+)['\"]",
                        r'(?:export\s+)?([A-Z_]{3,})\s*=',
                        r'GEMINI_API_KEY|OPENAI_API_KEY|ANTHROPIC_API_KEY|FIRECRAWL_API_KEY|NOTION_TOKEN|OPENSPACE_API_KEY',
                    ]
                    for p in patterns:
                        for m in re.finditer(p, content, re.IGNORECASE):
                            try:
                                var = m.group(1)
                            except IndexError:
                                continue
                            if var and len(var) > 2:
                                if var not in all_vars:
                                    all_vars[var] = []
                                all_vars[var].append(skill_dir.name)

        lines = [
            "# Skills Environment Variables Template",
            "# 复制此文件为 .env 并填入实际值: cp .env.template .env",
            f"# 生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
            "",
        ]

        # 分组输出
        api_keys = {k: v for k, v in all_vars.items() if any(w in k.upper() for w in ['KEY', 'TOKEN', 'SECRET'])}
        other_vars = {k: v for k, v in all_vars.items() if k not in api_keys}

        if api_keys:
            lines.append("# === API Keys / 密钥 ===")
            for var in sorted(api_keys.keys()):
                skills_using = ", ".join(all_vars[var])
                is_set = "✅" if os.environ.get(var) else "❌"
                set_value = os.environ.get(var, "")
                display_val = f"{set_value[:8]}..." if len(set_value) > 8 else set_value or "<未设置>"
                lines.append(f"# 用于: {skills_using}")
                lines.append(f"{var}={display_val}  [{is_set}]")
                lines.append("")
        if other_vars:
            lines.append("# === 其他环境变量 ===")
            for var in sorted(other_vars.keys()):
                skills_using = ", ".join(other_vars[var])
                lines.append(f"# 用于: {skills_using}")
                val = os.environ.get(var, "")
                lines.append(f'{var}="{val or ""}"')
                lines.append("")

        template_content = "\n".join(lines)

        if output_path:
            out = Path(output_path)
            out.parent.mkdir(parents=True, exist_ok=True)
            out.write_text(template_content, encoding='utf-8')
            print(f"✅ 环境变量模板已保存: {output_path}")
        else:
            print(template_content)

        return template_content

    # ================================================================
    #  内部方法
    # ================================================================

    def _fix_runtime(self, runtime: str, dry_run: bool) -> dict:
        """修复/安装运行时"""
        if self._tool_exists(runtime):
            return {"success": True, "message": f"`{runtime}` 已安装"}

        cmd = self._get_install_cmd(runtime)
        if not cmd:
            return {"success": False, "message": f"不知道如何自动安装 `{runtime}`"}

        if dry_run:
            return {"success": True, "message": f"[预览] 将执行: {cmd}"}

        print(f"🔧 正在安装 {runtime}...")
        try:
            result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=300)
            if result.returncode == 0:
                return {"success": True, "message": f"`{runtime}` 安装成功"}
            else:
                return {"success": False, "message": f"安装失败: {result.stderr[-200:]}"}
        except subprocess.TimeoutExpired:
            return {"success": False, "message": "安装超时"}
        except Exception as e:
            return {"success": False, "message": f"错误: {e}"}

    def _fix_deps(self, skill_name: str, dry_run: bool) -> dict:
        """修复指定 skill 的依赖"""
        if not skill_name:
            return {"success": False, "message": "请指定 skill 名称"}

        skill_path = self.skills_base / skill_name
        if not skill_path.exists():
            return {"success": False, "message": f"Skill 不存在: {skill_name}"}

        commands = []
        req_txt = skill_path / "requirements.txt"
        if req_txt.exists():
            commands.append(f"cd '{skill_path}' && pip3 install -r requirements.txt")

        pkg_json = skill_path / "package.json"
        if pkg_json.exists():
            commands.append(f"cd '{skill_path}' && npm install")

        if not commands:
            return {"success": True, "message": f"`{skill_name}` 无需安装额外依赖"}

        if dry_run:
            return {"success": True, "message": "[预览] 将执行:\n" + "\n".join(f"  $ {c}" for c in commands)}

        all_ok = True
        outputs = []
        for cmd in commands:
            print(f"📦 执行: {cmd}")
            try:
                r = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=120)
                if r.returncode != 0:
                    all_ok = False
                    outputs.append(f"失败: {r.stderr[-200:]}")
                else:
                    outputs.append("成功")
            except subprocess.TimeoutExpired:
                all_ok = False
                outputs.append("超时")
            except Exception as e:
                all_ok = False
                outputs.append(str(e))

        return {"success": all_ok, "message": "\n".join(outputs)}

    def _suggest_isolation(self, skill_name: str = "") -> dict:
        """为 skill 提供隔离方案"""
        suggestions = []
        target_dirs = [self.skills_base / skill_name] if skill_name else [
            d for d in self.skills_base.iterdir()
            if d.is_dir() and not d.name.startswith('.') and (d / "scripts").exists()
        ]

        for skill_path in target_dirs:
            name = skill_path.name
            has_py = any(skill_path.rglob("*.py"))
            has_ts_js = any(skill_path.rglob("*.ts")) or any(skill_path.rglob("*.js"))
            has_pkg = (skill_path / "package.json").exists()

            isolations = []

            if has_py and not (skill_path / ".venv").exists():
                isolations.append({
                    "type": "python_venv",
                    "cmd": f"cd '{skill_path}' && python3 -m venv .venv && source .venv/bin/activate && pip3 install -r requirements.txt",
                    "reason": "隔离 Python 依赖，避免版本冲突"
                })

            if has_ts_js and has_pkg and not (skill_path / "node_modules").exists():
                isolations.append({
                    "type": "node_local",
                    "cmd": f"cd '{skill_path}' && npm install",
                    "reason": "本地安装 Node.js 依赖"
                })

            if isolations:
                suggestions.append({"skill": name, "isolations": isolations})

        return {"success": True, "suggestions": suggestions}

    def _generate_env_template(self, dry_run: bool) -> dict:
        """生成环境变量模板的内部接口"""
        template = self.generate_env_template()
        return {"success": True, "message": f"\n{template}\n"}

    @staticmethod
    def _tool_exists(tool: str) -> bool:
        """检查工具是否存在"""
        try:
            if tool == 'chrome':
                r = subprocess.run(
                    ["/Applications/Google Chrome.app/Contents/MacOS/Google Chrome", "--version"],
                    capture_output=True, timeout=5
                )
                return r.returncode == 0
            r = subprocess.run([tool, "--version"], capture_output=True, timeout=5)
            return r.returncode == 0
        except (FileNotFoundError, OSError):
            return False

    @staticmethod
    def _pip_installed(package: str) -> bool:
        """检查 Python 包是否已安装"""
        try:
            r = subprocess.run(
                ["pip3", "show", package],
                capture_output=True, timeout=10
            )
            return r.returncode == 0
        except Exception:
            return False

    @staticmethod
    def _get_install_cmd(tool: str) -> Optional[str]:
        """获取工具安装命令"""
        cmds = {
            "uv": "curl -LsSf https://astral.sh/uv/install.sh | sh",
            "bun": "curl -fsSL https://bun.sh/install | bash",
            "npx": "brew install node  # npx 随 Node.js 一起安装",
            "pnpm": "npm install -g pnpm",
            "playwright": "pip3 install playwright && playwright install chromium",
            "chrome": None,  # 手动下载
            "node": "brew install node",
            "npm": "brew install node",
        }
        return cmds.get(tool)


def main():
    import argparse

    default_skills = str(Path.home() / ".workbuddy" / "skills")

    parser = argparse.ArgumentParser(description="Skills Fix Engine - 自动修复引擎")
    subparsers = parser.add_subparsers(dest="command", help="可用命令")

    # check 子命令
    check_parser = subparsers.add_parser("check", help="全面检查可修复项")
    check_parser.add_argument("--path", type=str, default=default_skills)

    # fix 子命令
    fix_parser = subparsers.add_parser("fix", help="执行修复")
    fix_parser.add_argument("type", choices=["runtime", "deps", "env_template", "isolate"],
                           help="修复类型")
    fix_parser.add_argument("target", nargs="?", default="", help="目标 (运行时名或 skill 名)")
    fix_parser.add_argument("--path", type=str, default=default_skills)
    fix_parser.add_argument("--dry-run", action="store_true", help="仅预览不执行")
    fix_parser.add_argument("-y", "--yes", action="store_true", help="跳过确认直接执行")

    # env-template 子命令
    env_parser = subparsers.add_parser("env-template", help="生成环境变量模板")
    env_parser.add_argument("--path", type=str, default=default_skills)
    env_parser.add_argument("-o", "--output", type=str, help="输出文件路径")

    args = parser.parse_args()

    engine = SkillsFixEngine(args.path)

    if args.command == "check":
        results = engine.check_all()
        print("\n=== 🔍 环境检查报告 ===\n")

        if results["missing_runtimes"]:
            print("📦 缺失的运行时:")
            for rt in results["missing_runtimes"]:
                pri = "🔴 高" if rt['priority'] == 'high' else "🟡 中"
                print(f"  - `{rt['name']}` [{pri}]: {rt['install_cmd']}")

        if results["missing_deps"]:
            print("\n📋 缺失依赖的 Skills:")
            for skill, info in results["missing_deps"].items():
                pkgs = info.get('packages', info.get('sample_packages', []))
                print(f"  - `{skill}` ({info['type']}): {', '.join(pkgs[:5])}")
                print(f"    修复: {info['fix_cmd']}")

        no_issues = (not results["missing_runtimes"] and not results["missing_deps"])
        if no_issues:
            print("✅ 未发现需要立即修复的问题！")

    elif args.command == "fix":
        if args.dry_run:
            print("👀 **DRY RUN 模式** — 仅预览，不会执行任何操作\n")

        result = engine.auto_fix(args.type, args.target, dry_run=args.dry_run)
        status = "✅" if result["success"] else "❌"
        print(f"{status} {result.get('message', '')}")

    elif args.command == "env-template":
        engine.generate_env_template(args.output)

    else:
        # 默认：显示帮助和快速检查
        print("""
╔══════════════════════════════════════════════╗
║   🛠️  Skills Fix Engine - 自动修复引擎       ║
║                                              ║
║   可用命令:                                   ║
║   • check              全面检查可修复项       ║
║   • fix <type> [target]  执行修复             ║
║     types: runtime, deps, env_template,      ║
║            isolate                            ║
║   • env-template       生成环境变量模板       ║
║                                              ║
║   示例:                                       ║
║   python fixer.py check                      ║
║   python fixer.py fix runtime uv --dry-run   ║
║   python fixer.py fix deps url-reader         ║
║   python fixer.py env-template               ║
╚══════════════════════════════════════════════╝
""")
        # 快速展示
        results = engine.check_all()
        issue_count = len(results["missing_runtimes"]) + len(results["missing_deps"])
        if issue_count > 0:
            print(f"⚠️ 发现 {issue_count} 个可修复项 — 运行 `check` 查看详情\n")


if __name__ == "__main__":
    main()
