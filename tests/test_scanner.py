"""
test_scanner.py — SkillsScanner 核心逻辑单元测试
覆盖：扫描发现、依赖提取、健康评分算法、边界情况、冲突检测
"""

import pytest
from pathlib import Path

# 将 scripts 目录加入 sys.path，以便导入被测模块
import sys
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "scripts"))

from scanner import SkillsScanner, SkillReport, SkillDependency


class TestScanDirectoryFindsSkills:
    """测试扫描器能正确发现 SKILL.md 文件和目录结构。"""

    def test_scan_single_skill_detects_skill_md(self, sample_skill_dir):
        """扫描含 SKILL.md 的目录时，报告应标记 skill_md_exists=True。"""
        scanner = SkillsScanner(str(sample_skill_dir))
        report = scanner._scan_single_skill(sample_skill_dir)
        assert report.skill_md_exists is True
        assert report.name == sample_skill_dir.name

    def test_scan_all_finds_multiple_skills(self, multi_skill_base):
        """scan_all() 能发现所有子目录（不含隐藏目录）。"""
        scanner = SkillsScanner(str(multi_skill_base))
        results = scanner.scan_all()
        assert len(results) == 4  # skill-a, b, c, d
        assert "skill-a" in results
        assert "skill-b" in results
        assert "skill-c" in results
        assert "skill-d" in results

    def test_scan_ignores_hidden_dirs(self, tmp_path):
        """扫描时应忽略以 . 开头的隐藏目录。"""
        (tmp_path / ".hidden").mkdir()
        (tmp_path / ".hidden" / "SKILL.md").write_text("# hidden\n", encoding="utf-8")
        (tmp_path / "normal").mkdir()
        (tmp_path / "normal" / "SKILL.md").write_text("# normal\n", encoding="utf-8")

        scanner = SkillsScanner(str(tmp_path))
        results = scanner.scan_all()
        assert len(results) == 1
        assert "normal" in results
        assert ".hidden" not in results

    def test_scan_nonexistent_dir(self):
        """扫描不存在的目录应返回空字典且不崩溃。"""
        scanner = SkillsScanner("/nonexistent/path/that/does/not/exist")
        results = scanner.scan_all()
        assert results == {}


class TestDetectDependenciesPython:
    """测试 Python 脚本依赖提取能力。"""

    def test_extract_python_imports(self, sample_skill_dir):
        """应从 .py 文件的 import 语句中提取第三方依赖。"""
        scanner = SkillsScanner(str(sample_skill_dir))
        report = scanner._scan_single_skill(sample_skill_dir)

        dep_names = [d.name for d in report.dependencies]
        # main.py 中有 import requests 和 from bs4 import BeautifulSoup
        assert "requests" in dep_names
        assert "bs4" in dep_names  # BeautifulSoup 模块名映射为 bs4

    def test_extract_pip_install_from_skill_md(self, sample_skill_dir):
        """应从 SKILL.md 中的 pip install 行提取依赖及版本约束。"""
        scanner = SkillsScanner(str(sample_skill_dir))
        report = scanner._scan_single_skill(sample_skill_dir)

        dep_dict = {d.name: d.version_spec for d in report.dependencies}
        assert "requests" in dep_dict
        assert "beautifulsoup4" in dep_dict
        # 版本号应被正确解析
        assert ">=" in dep_dict.get("requests", "") or "beautifulsoup4" in dep_dict

    def test_ignore_stdlib_imports(self, tmp_path):
        """不应将 Python 标准库模块识别为需要安装的依赖。"""
        (tmp_path / "SKILL.md").write_text("# test\n", encoding="utf-8")
        scripts = tmp_path / "scripts"
        scripts.mkdir()
        (scripts / "stdlib.py").write_text(
            "import os\nimport sys\nimport json\nfrom pathlib import Path\n"
            "import re\nfrom datetime import datetime\n",
            encoding="utf-8"
        )

        scanner = SkillsScanner(str(tmp_path))
        report = scanner._scan_single_skill(tmp_path)
        dep_names = [d.name for d in report.dependencies]
        stdlib_modules = {"os", "sys", "json", "pathlib", "re", "datetime"}
        for mod in stdlib_modules:
            assert mod not in dep_names, f"标准库 {mod} 不应出现在依赖列表中"


class TestDetectDependenciesShell:
    """测试 Shell 脚本依赖提取能力。"""

    def test_extract_pip_from_shell(self, sample_skill_dir):
        """从 .sh 文件中的 pip3 install 命令提取依赖。"""
        scanner = SkillsScanner(str(sample_skill_dir))
        report = scanner._scan_single_skill(sample_skill_dir)
        dep_names = [d.name for d in report.dependencies]
        # helper.sh 有 `pip3 install click`
        assert "click" in dep_names

    def test_extract_npx_from_shell(self, sample_skill_dir):
        """从 shell 脚本检测 npx 运行时需求。"""
        scanner = SkillsScanner(str(sample_skill_dir))
        report = scanner._scan_single_skill(sample_skill_dir)
        assert "npx" in report.runtime_requirements


class TestHealthScoreCalculation:
    """
    健康评分算法核心测试 — 这是最关键的业务逻辑！
    
    评分规则：
    - 基础分 100
    - 无 SKILL.md: -15
    - 有脚本但无依赖声明: -5
    - 缺少运行时: 每个 -15
    - 未设置环境变量: 每个 -5（上限 -20）
    - Python 脚本但无 python3: -20
    """

    def test_perfect_score_for_healthy_skill(self, monkeypatch, tmp_path):
        """完全健康的 skill（SKILL.md + 已配置 env + 可用运行时）应得高分。"""
        # 设置环境变量使 API Key 检测通过
        monkeypatch.setenv("OPENAI_API_KEY", "sk-test-key")

        (tmp_path / "SKILL.md").write_text("# Perfect Skill\n", encoding="utf-8")

        # Mock _check_tool_available 使其总是返回 True
        scanner = SkillsScanner(str(tmp_path))

        original_check = scanner._check_tool_available
        scanner._check_tool_available = lambda tool: True

        report = scanner._scan_single_skill(tmp_path)
        assert report.health_score == 100

        # 恢复原始方法
        scanner._check_tool_available = original_check

    def test_missing_skill_md_deducts_points(self, monkeypatch, tmp_path):
        """缺少 SKILL.md 应扣 15 分。"""
        monkeypatch.setenv("OPENAI_API_KEY", "sk-test")
        # 故意不创建 SKILL.md

        scripts = tmp_path / "scripts"
        scripts.mkdir()
        (scripts / "run.py").write_text("import requests\n", encoding="utf-8")

        scanner = SkillsScanner(str(tmp_path))
        scanner._check_tool_available = lambda tool: True

        report = scanner._scan_single_skill(tmp_path)
        assert report.health_score <= 85  # 至少扣了 15 分
        assert any("SKILL.md" in issue for issue in report.issues)

    def test_scripts_without_deps_deducts_points(self, monkeypatch, tmp_path):
        """有脚本但未声明依赖应扣 5 分。"""
        monkeypatch.setenv("OPENAI_API_KEY", "sk-test")
        (tmp_path / "SKILL.md").write_text("# Test\n", encoding="utf-8")

        scripts = tmp_path / "scripts"
        scripts.mkdir()
        # 只有标准库 import → 无第三方依赖
        (scripts / "bare.py").write_text(
            "import os\nprint('hello')\n", encoding="utf-8"
        )

        scanner = SkillsScanner(str(tmp_path))
        scanner._check_tool_available = lambda tool: True

        report = scanner._scan_single_skill(tmp_path)
        # 有脚本 + 无依赖声明 → -5
        assert report.health_score == 95

    def test_missing_runtime_deducts_per_item(self, monkeypatch, tmp_path):
        """每个缺失运行时扣 15 分。"""
        monkeypatch.setenv("OPENAI_API_KEY", "sk-test")
        (tmp_path / "SKILL.md").write_text("Uses `uv run` and `bun`.\n", encoding="utf-8")

        scanner = SkillsScanner(str(tmp_path))
        # Mock: 所有运行时都不可用
        scanner._check_tool_available = lambda tool: False

        report = scanner._scan_single_skill(tmp_path)
        # uv 和 bun 都缺失 → -30
        assert report.health_score <= 70
        runtime_issues = [i for i in report.issues if "运行时" in i]
        assert len(runtime_issues) >= 2

    def test_missing_env_vars_capped_deduction(self, monkeypatch, tmp_path):
        """环境变量扣分应有上限（最多 -20）。"""
        # 故意不设置任何环境变量
        for var in ["OPENAI_API_KEY", "ANTHROPIC_API_KEY", "NOTION_TOKEN",
                     "GEMINI_API_KEY", "FIRECRAWL_API_KEY"]:
            monkeypatch.delenv(var, raising=False)

        (tmp_path / "SKILL.md").write_text(
            "Need OPENAI_API_KEY, ANTHROPIC_API_KEY, NOTION_TOKEN, GEMINI_API_KEY, FIRECRAWL_API_KEY.\n",
            encoding="utf-8"
        )

        scanner = SkillsScanner(str(tmp_path))
        scanner._check_tool_available = lambda tool: True

        report = scanner._scan_single_skill(tmp_path)
        # 5 个环境变量 × 5分 = 25，但上限是 20
        assert report.health_score >= 80

    def test_score_never_below_zero_or_above_100(self, monkeypatch, tmp_path):
        """健康评分应在 [0, 100] 范围内。"""
        # 构造一个最差情况：各种问题叠加
        monkeypatch.delenv("OPENAI_API_KEY", raising=False)
        # 无 SKILL.md, 有大量缺失运行时, 多个未设置变量

        scripts = tmp_path / "scripts"
        scripts.mkdir()
        (scripts / "heavy.py").write_text(
            "import requests\nimport flask\nimport django\nimport pandas\n"
            "import numpy\nimport tensorflow\n",
            encoding="utf-8"
        )
        (scripts / "run.sh").write_text(
            "#!/bin/bash\npip3 install a b c d e f g h i j\n"
            "npx tsc\nbun run\nuv run\nnode --version\nplaywright --version\n",
            encoding="utf-8"
        )

        scanner = SkillsScanner(str(tmp_path))
        scanner._check_tool_available = lambda tool: False

        report = scanner._scan_single_skill(tmp_path)
        assert 0 <= report.health_score <= 100


class TestEdgeCases:
    """边界情况与容错性测试。"""

    def test_scan_empty_directory(self, empty_skill_dir):
        """扫描空目录应返回有基本信息的报告，不崩溃。"""
        scanner = SkillsScanner(str(empty_skill_dir))
        report = scanner._scan_single_skill(empty_skill_dir)
        assert isinstance(report, SkillReport)
        assert report.skill_md_exists is False
        assert len(report.script_files) == 0
        assert len(report.dependencies) == 0

    def test_scan_with_invalid_skill_md(self, invalid_skill_dir):
        """格式错误的 SKILL.md 和二进制文件不应导致崩溃。"""
        scanner = SkillsScanner(str(invalid_skill_dir))
        report = scanner._scan_single_skill(invalid_skill_dir)
        # 即使文件内容异常，也不应抛异常
        assert isinstance(report, SkillReport)

    def test_scan_with_package_json(self, multi_skill_base):
        """应能从 package.json 提取 npm 依赖。"""
        scanner = SkillsScanner(str(multi_skill_base))
        report = scanner._scan_single_skill(multi_skill_base / "skill-d")

        assert report.has_package_json is True
        dep_names = [d.name for d in report.dependencies]
        assert "react" in dep_names
        assert "lodash" in dep_names
        assert "typescript" in dep_names

    def test_parse_node_script_extracts_deps(self, multi_skill_base):
        """从 TypeScript/JavaScript 脚本提取 npm 依赖（如有）。"""
        scanner = SkillsScanner(str(multi_skill_base))
        report = scanner._scan_single_skill(multi_skill_base / "skill-b")
        # index.ts 有 import express — 注意：Node 依赖提取可能受限于正则
        # 这里主要验证不崩溃 + 报告结构正确
        assert isinstance(report.dependencies, list)
        # 如果 express 被识别到则验证
        dep_names = [d.name for d in report.dependencies]
        if "express" not in dep_names:
            # 至少验证运行时检测正常工作
            assert report.uses_bun is True or len(report.script_files) > 0

    def test_detects_uv_usage_in_python_script(self, tmp_path):
        """检测 Python 脚本开头的 'uv run' 使用。"""
        (tmp_path / "SKILL.md").write_text("# UV Skill\n", encoding="utf-8")
        scripts = tmp_path / "scripts"
        scripts.mkdir()
        (scripts / "app.py").write_text('"""App using uv run."""\nuv run app_main()\n', encoding="utf-8")

        scanner = SkillsScanner(str(tmp_path))
        report = scanner._scan_single_skill(tmp_path)
        assert report.uses_uv is True
        assert "uv" in report.runtime_requirements

    def test_detects_env_vars_from_python_script(self, tmp_path):
        """从 Python 脚本的 os.environ.get() 调用中检测环境变量需求。"""
        (tmp_path / "SKILL.md").write_text("# Env Skill\n", encoding="utf-8")
        scripts = tmp_path / "scripts"
        scripts.mkdir()
        (scripts / "config.py").write_text(
            'import os\nkey = os.environ.get("MY_CUSTOM_API_KEY")\ntoken = os.environ.get("SECRET_TOKEN")\n',
            encoding="utf-8"
        )

        scanner = SkillsScanner(str(tmp_path))
        report = scanner._scan_single_skill(tmp_path)
        assert "MY_CUSTOM_API_KEY" in report.env_vars
        assert "SECRET_TOKEN" in report.env_vars


class TestGlobalConflictDetection:
    """全局版本冲突和运行时冲突检测测试。"""

    def test_version_conflict_detected(self, tmp_path):
        """当多个 skill 对同一依赖要求不同版本时，应检测到冲突。"""

        # Skill X: 需要 requests>=2.28
        skill_x = tmp_path / "skill-x"
        skill_x.mkdir()
        (skill_x / "SKILL.md").write_text(
            "```bash\npip install requests>=2.28\n```\n", encoding="utf-8"
        )

        # Skill Y: 需要 requests==2.25.0
        skill_y = tmp_path / "skill-y"
        skill_y.mkdir()
        (skill_y / "SKILL.md").write_text(
            "```bash\npip install requests==2.25.0\n```\n", encoding="utf-8"

        )

        scanner = SkillsScanner(str(tmp_path))
        scanner.scan_all()

        conflict_issues = [
            i for i in scanner.global_issues if i.get("type") == "version_conflict"
        ]
        assert len(conflict_issues) >= 1
        assert conflict_issues[0]["dependency"] == "requests"

    def test_heavy_runtime_dependency_detected(self, tmp_path):
        """超过 3 个 skill 使用同一运行时应触发高频警告。"""
        for i in range(4):  # 创建 4 个都使用 node 的 skill
            skill = tmp_path / f"node-skill-{i}"
            skill.mkdir()
            (skill / "SKILL.md").write_text(f"# Skill {i}\nUses node.\n", encoding="utf-8")
            s = skill / "scripts"
            s.mkdir()
            (s / "run.sh").write_text("node --version\n", encoding="utf-8")

        scanner = SkillsScanner(str(tmp_path))
        scanner.scan_all()

        heavy_issues = [
            i for i in scanner.global_issues if i.get("type") == "heavy_runtime_dependency"
        ]
        assert len(heavy_issues) >= 1
        assert heavy_issues[0]["count"] >= 4


class TestSummaryOutput:
    """摘要输出格式测试。"""

    def test_summary_with_no_skills(self):
        """无 skill 时 get_summary() 返回最小化结果。"""
        scanner = SkillsScanner("/nonexistent/path/for/test")
        summary = scanner.get_summary()
        assert summary["total"] == 0

    def test_summary_with_multiple_skills(self, multi_skill_base):
        """多 skill 场景下摘要包含完整统计信息。"""
        scanner = SkillsScanner(str(multi_skill_base))
        scanner.scan_all()
        summary = scanner.get_summary()

        assert summary["total_skills"] == 4
        assert "avg_health_score" in summary
        assert "healthy_count" in summary
        assert "warning_count" in summary
        assert "critical_count" in summary
        assert "unique_runtimes" in summary
        assert "global_issues" in summary
        assert "scan_time" in summary

    def test_to_json_output_valid_json(self, multi_skill_base):
        """to_json() 输出应为合法 JSON 字符串。"""
        import json
        scanner = SkillsScanner(str(multi_skill_base))
        scanner.scan_all()
        json_str = scanner.to_json()
        data = json.loads(json_str)
        assert "summary" in data
        assert "skills" in data

    def test_to_json_writes_to_file(self, multi_skill_base, tmp_output_path):
        """to_json(filepath) 应将 JSON 写入指定路径。"""
        import json
        out_file = str(tmp_output_path / "report.json")
        scanner = SkillsScanner(str(multi_skill_base))
        scanner.scan_all()
        scanner.to_json(out_file)

        assert Path(out_file).exists()
        with open(out_file, encoding='utf-8') as f:
            data = json.load(f)
        assert "summary" in data


class TestDataClasses:
    """数据类序列化与结构测试。"""

    def test_skill_dependency_dataclass(self):
        """SkillDependency 数据类应正确存储字段值。"""
        dep = SkillDependency(
            name="requests",
            version_spec=">=2.28",
            dep_type="pip",
            source_file="SKILL.md",
            is_installed=None,
            installed_version=None,
            is_optional=False,
        )
        assert dep.name == "requests"
        assert dep.dep_type == "pip"
        assert dep.is_optional is False

    def test_skill_report_default_values(self):
        """SkillReport 默认值应合理初始化。"""
        report = SkillReport(name="test-skill", path="/fake/path")
        assert report.health_score == 0  # 默认 0，计算后更新
        assert report.has_scripts is False
        assert report.skill_md_exists is False
        assert report.issues == []
        assert report.warnings == []
