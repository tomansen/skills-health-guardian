"""
test_cli_extra.py — CLI 额外测试用例
补充边界情况和特殊场景的测试
"""

import sys
from pathlib import Path
from unittest.mock import patch, MagicMock

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "scripts"))

from cli import (
    format_table,
    format_quiet,
    format_json_output,
    format_markdown_output,
    main,
)
from scanner import SkillsScanner, SkillReport


# ============================================================
#  边界情况和特殊场景测试
# ============================================================

class TestMainEdgeCases:
    """main 函数的边界情况测试"""

    def test_format_markdown_with_real_scanner(self, tmp_path):
        """markdown 输出应能正确生成报告"""
        # 创建一个真实的 scanner 实例
        scanner = SkillsScanner(str(tmp_path))
        scanner.skills = {
            "test-skill": SkillReport(
                name="test-skill",
                path=str(tmp_path / "test-skill"),
                health_score=85,
                issues=[],
                warnings=["Minor warning"],
                dependencies=[],
                runtime_requirements=[],
                env_vars=[],
                script_files=["scripts/main.py"],
                skill_md_exists=True,
            )
        }
        # 添加 summary 数据
        scanner.get_summary = MagicMock(return_value={
            "total_skills": 1,
            "avg_health_score": 85,
            "healthy_count": 1,
            "warning_count": 0,
            "critical_count": 0,
            "total_dependencies": 0,
            "scan_time": "2026-04-14T09:00:00",
        })

        result = format_markdown_output(scanner)
        assert isinstance(result, str)
        assert len(result) > 0

    @patch("cli.argparse.ArgumentParser.parse_args")
    @patch("cli.format_markdown_output", return_value="## Markdown Report")
    @patch("cli.SkillsScanner")
    def test_main_markdown_format(self, mock_scanner_cls, mock_fmt, mock_parse, capsys):
        """markdown 格式应正确输出"""
        scanner_instance = MagicMock()
        scanner_instance.skills = {}
        scanner_instance.get_summary.return_value = {"total_skills": 0}
        mock_scanner_cls.return_value = scanner_instance
        mock_parse.return_value = MagicMock(
            watch=None, skill=None, format="markdown",
            output=None, output_dir="", verbose=False,
            skip_fix=True, dry_run=False, no_color=False,
        )
        main()
        captured = capsys.readouterr()
        assert "## Markdown Report" in captured.out

    @patch("cli.argparse.ArgumentParser.parse_args")
    @patch("cli.format_table", return_value="TABLE")
    @patch("cli.SkillsScanner")
    def test_main_default_fallback_format(self, mock_scanner_cls, mock_fmt, mock_parse, capsys):
        """未知格式应回退到 table 格式"""
        scanner_instance = MagicMock()
        scanner_instance.skills = {}
        scanner_instance.get_summary.return_value = {"total_skills": 0}
        mock_scanner_cls.return_value = scanner_instance
        mock_parse.return_value = MagicMock(
            watch=None, skill=None, format="unknown",
            output=None, output_dir="", verbose=False,
            skip_fix=True, dry_run=False, no_color=False,
        )
        main()
        captured = capsys.readouterr()
        assert "TABLE" in captured.out

    @patch("cli.argparse.ArgumentParser.parse_args")
    @patch("cli.format_json_output", return_value='{"test": true}')
    @patch("cli.SkillsScanner")
    def test_main_output_file_json_no_duplicate(self, mock_scanner_cls, mock_fmt, mock_parse, tmp_path, capsys):
        """json 格式输出到文件时不应重复打印到 stdout"""
        scanner_instance = MagicMock()
        scanner_instance.skills = {}
        scanner_instance.get_summary.return_value = {"total_skills": 0}
        mock_scanner_cls.return_value = scanner_instance
        out_file = str(tmp_path / "report.json")
        mock_parse.return_value = MagicMock(
            watch=None, skill=None, format="json",
            output=out_file, output_dir="", verbose=False,
            skip_fix=True, dry_run=False, no_color=False,
        )
        main()
        captured = capsys.readouterr()
        # json 格式不应该重复打印到 stdout
        assert captured.out.count('{"test": true}') <= 1

    @patch("cli.argparse.ArgumentParser.parse_args")
    @patch("cli.format_quiet", return_value="quiet")
    @patch("cli.SkillsScanner")
    def test_main_output_file_quiet_no_duplicate(self, mock_scanner_cls, mock_fmt, mock_parse, tmp_path, capsys):
        """quiet 格式输出到文件时不应重复打印到 stdout"""
        scanner_instance = MagicMock()
        scanner_instance.skills = {}
        scanner_instance.get_summary.return_value = {"total_skills": 0}
        mock_scanner_cls.return_value = scanner_instance
        out_file = str(tmp_path / "report.txt")
        mock_parse.return_value = MagicMock(
            watch=None, skill=None, format="quiet",
            output=out_file, output_dir="", verbose=False,
            skip_fix=True, dry_run=False, no_color=False,
        )
        main()
        captured = capsys.readouterr()
        # quiet 格式不应该重复打印到 stdout
        assert captured.out.count("quiet") <= 1


class TestFormatTableEdgeCases:
    """format_table 的边界情况测试"""

    def test_format_table_empty_skills(self, tmp_path):
        """空 skills 列表应正确处理"""
        scanner = SkillsScanner(str(tmp_path))
        scanner.skills = {}
        scanner.get_summary = MagicMock(return_value={
            "total_skills": 0,
            "avg_health_score": 0,
            "healthy_count": 0,
            "warning_count": 0,
            "critical_count": 0,
            "total_dependencies": 0,
            "scan_time": "2026-04-14T09:00:00",
        })
        result = format_table(scanner)
        assert isinstance(result, str)
        assert len(result) > 0

    def test_format_table_long_skill_name(self, tmp_path):
        """超长 skill 名称应正确截断"""
        scanner = SkillsScanner(str(tmp_path))
        long_name = "very-long-skill-name-that-exceeds-maximum-length-allowed-in-table-display"
        scanner.skills = {
            long_name: SkillReport(
                name=long_name,
                path=str(tmp_path),
                health_score=90,
                issues=[],
                warnings=[],
                dependencies=[],
                runtime_requirements=[],
                env_vars=[],
                script_files=["scripts/main.py"],
                skill_md_exists=True,
            )
        }
        scanner.get_summary = MagicMock(return_value={
            "total_skills": 1,
            "avg_health_score": 90,
            "healthy_count": 1,
            "warning_count": 0,
            "critical_count": 0,
            "total_dependencies": 0,
            "scan_time": "2026-04-14T09:00:00",
        })
        result = format_table(scanner)
        assert isinstance(result, str)
        # 名称应该被截断但不会导致格式错误

    def test_format_table_many_dependencies(self, tmp_path):
        """verbose 模式下多个依赖应正确显示"""
        scanner = SkillsScanner(str(tmp_path))
        # 创建多个 mock 依赖，确保 name 返回字符串
        class MockDependency:
            def __init__(self, name):
                self.name = name

        deps = [MockDependency(f"dep{i}") for i in range(10)]
        scanner.skills = {
            "multi-dep-skill": SkillReport(
                name="multi-dep-skill",
                path=str(tmp_path),
                health_score=85,
                issues=[],
                warnings=[],
                dependencies=deps,
                runtime_requirements=[],
                env_vars=[],
                script_files=["scripts/main.py"],
                skill_md_exists=True,
            )
        }
        scanner.get_summary = MagicMock(return_value={
            "total_skills": 1,
            "avg_health_score": 85,
            "healthy_count": 1,
            "warning_count": 0,
            "critical_count": 0,
            "total_dependencies": 10,
            "scan_time": "2026-04-14T09:00:00",
        })
        result = format_table(scanner, verbose=True)
        assert isinstance(result, str)
        # 应该显示依赖信息
        assert "Deps:" in result or "deps:" in result

    def test_format_table_with_global_issues(self, tmp_path):
        """全局问题应正确显示"""
        scanner = SkillsScanner(str(tmp_path))
        scanner.skills = {
            "test-skill": SkillReport(
                name="test-skill",
                path=str(tmp_path),
                health_score=70,
                issues=[],
                warnings=[],
                dependencies=[],
                runtime_requirements=[],
                env_vars=[],
                script_files=["scripts/main.py"],
                skill_md_exists=True,
            )
        }
        scanner.get_summary = MagicMock(return_value={
            "total_skills": 1,
            "avg_health_score": 70,
            "healthy_count": 0,
            "warning_count": 1,
            "critical_count": 0,
            "total_dependencies": 0,
            "scan_time": "2026-04-14T09:00:00",
            "global_issues": [
                {"type": "version_conflict", "dependency": "requests", "count": 2},
                {"type": "heavy_runtime_dependency", "runtime": "node", "count": 5},
            ]
        })
        result = format_table(scanner)
        assert isinstance(result, str)
        assert "Global Issues" in result or "global_issues" in result


class TestFormatJsonEdgeCases:
    """format_json_output 的边界情况测试"""

    def test_format_json_empty_skills(self, tmp_path):
        """空 skills 列表应生成有效 JSON"""
        scanner = SkillsScanner(str(tmp_path))
        scanner.skills = {}
        scanner.get_summary = MagicMock(return_value={
            "total_skills": 0,
            "avg_health_score": 0,
            "healthy_count": 0,
            "warning_count": 0,
            "critical_count": 0,
            "total_dependencies": 0,
            "scan_time": "2026-04-14T09:00:00",
        })
        result = format_json_output(scanner)
        import json
        data = json.loads(result)
        assert isinstance(data, dict)
        assert "skills" in data
        assert isinstance(data["skills"], dict)
        assert len(data["skills"]) == 0


class TestFormatQuietEdgeCases:
    """format_quiet 的边界情况测试"""

    def test_format_quiet_empty_skills(self, tmp_path):
        """空 skills 列表应正确生成摘要"""
        scanner = SkillsScanner(str(tmp_path))
        scanner.skills = {}
        scanner.get_summary = MagicMock(return_value={
            "total_skills": 0,
            "avg_health_score": 0,
            "healthy_count": 0,
            "warning_count": 0,
            "critical_count": 0,
            "total_dependencies": 0,
            "scan_time": "2026-04-14T09:00:00",
        })
        result = format_quiet(scanner)
        assert isinstance(result, str)
        assert "SHG score=0.0" in result
        assert "ok=0" in result
        assert "warn=0" in result
        assert "crit=0" in result
        assert "total=0" in result
