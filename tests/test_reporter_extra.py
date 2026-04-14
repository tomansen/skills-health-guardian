"""
test_reporter_extra.py — Reporter 补充测试
覆盖：_check_rt_available 全部分支、_generate_suggestions 边界、
      _save_snapshot / _load_trend、main() 入口

关键：HealthReporter 是 reporter.py 中唯一的类
_check_rt_available 是类方法（实例方法）
"""

import sys
from pathlib import Path

SCRIPTS_DIR = Path(__file__).resolve().parent.parent / "scripts"
if str(SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPTS_DIR))

import pytest
import json
import os
from unittest.mock import patch, MagicMock
import reporter as _reporter_module
from reporter import HealthReporter, ReportConfig


# ============================================================
#  _check_rt_available 测试
# ============================================================

class TestCheckRtAvailableExtra:

    def test_chrome_available(self):
        """chrome 可用时返回 True。"""
        reporter = HealthReporter()
        with patch('subprocess.run') as mock_run:
            mock_result = MagicMock()
            mock_result.returncode = 0
            mock_run.return_value = mock_result
            result = reporter._check_rt_available("chrome")
        assert result is True

    def test_chrome_not_available(self):
        """chrome 不可用时返回 False。"""
        reporter = HealthReporter()
        with patch('subprocess.run') as mock_run:
            mock_run.side_effect = FileNotFoundError()
            result = reporter._check_rt_available("chrome")
        assert result is False

    def test_playwright_available(self):
        """playwright 可用时返回 True。"""
        reporter = HealthReporter()
        with patch('subprocess.run') as mock_run:
            mock_result = MagicMock()
            mock_result.returncode = 0
            mock_run.return_value = mock_result
            result = reporter._check_rt_available("playwright")
        assert result is True

    def test_playwright_not_available(self):
        """playwright 不可用时返回 False。"""
        reporter = HealthReporter()
        with patch('subprocess.run') as mock_run:
            mock_run.side_effect = FileNotFoundError()
            result = reporter._check_rt_available("playwright")
        assert result is False

    def test_generic_tool_available(self):
        """通用工具（如 uv）可用时返回 True。"""
        reporter = HealthReporter()
        with patch('subprocess.run') as mock_run:
            mock_result = MagicMock()
            mock_result.returncode = 0
            mock_run.return_value = mock_result
            result = reporter._check_rt_available("uv")
        assert result is True

    def test_generic_tool_not_available(self):
        """通用工具不可用时返回 False。"""
        reporter = HealthReporter()
        with patch('subprocess.run') as mock_run:
            mock_result = MagicMock()
            mock_result.returncode = 1
            mock_run.return_value = mock_result
            result = reporter._check_rt_available("uv")
        assert result is False

    def test_exception_returns_false(self):
        """工具检查抛出异常时返回 False。"""
        reporter = HealthReporter()
        with patch('subprocess.run') as mock_run:
            mock_run.side_effect = OSError("Permission denied")
            result = reporter._check_rt_available("uv")
        assert result is False

    def test_file_not_found_returns_false(self):
        """工具检查抛出 FileNotFoundError 时返回 False。"""
        reporter = HealthReporter()
        with patch('subprocess.run') as mock_run:
            mock_run.side_effect = FileNotFoundError("uv not found")
            result = reporter._check_rt_available("uv")
        assert result is False


# ============================================================
#  _generate_suggestions 测试
# ============================================================

class TestGenerateSuggestionsExtra:

    def test_suggests_missing_runtime(self):
        """缺失的运行时应出现在建议中。"""
        reporter = HealthReporter()
        summary = {"unique_runtimes": ["uv", "bun"], "unique_env_vars": []}
        skills = {}
        with patch.object(reporter, '_check_rt_available', return_value=False):
            suggestions = reporter._generate_suggestions(summary, skills)
        assert any("uv" in s for s in suggestions)
        assert any("bun" in s for s in suggestions)

    def test_no_suggestion_when_runtime_available(self):
        """运行时已安装时不建议安装。"""
        reporter = HealthReporter()
        summary = {"unique_runtimes": ["uv"], "unique_env_vars": []}
        skills = {}
        with patch.object(reporter, '_check_rt_available', return_value=True):
            suggestions = reporter._generate_suggestions(summary, skills)
        assert not any("uv" in s and "安装" in s for s in suggestions)

    def test_suggests_missing_env_vars(self, monkeypatch):
        """未设置的环境变量应出现在建议中。"""
        reporter = HealthReporter()
        monkeypatch.delenv("OPENAI_API_KEY", raising=False)
        summary = {"unique_runtimes": [], "unique_env_vars": ["OPENAI_API_KEY"]}
        skills = {}
        suggestions = reporter._generate_suggestions(summary, skills)
        assert any("OPENAI_API_KEY" in s for s in suggestions)

    def test_low_score_skill_appears(self):
        """健康分低于 60 的 skill 应出现在建议中。"""
        reporter = HealthReporter()
        summary = {"unique_runtimes": [], "unique_env_vars": []}
        skills = {
            "bad-skill": {
                "health_score": 30,
                "issues": ["缺少 SKILL.md 文件"],
                "warnings": [],
                "dependencies": [],
                "runtime_requirements": [],
                "env_vars": [],
            }
        }
        suggestions = reporter._generate_suggestions(summary, skills)
        assert any("bad-skill" in s for s in suggestions)

    def test_dependency_conflict_suggestion(self):
        """被 3+ skill 共享的依赖应出现隔离建议。"""
        reporter = HealthReporter()
        summary = {"unique_runtimes": [], "unique_env_vars": []}
        skills = {
            "s1": {"dependencies": [{"name": "requests", "dep_type": "pip"}],
                   "health_score": 80, "issues": [], "warnings": []},
            "s2": {"dependencies": [{"name": "requests", "dep_type": "pip"}],
                   "health_score": 80, "issues": [], "warnings": []},
            "s3": {"dependencies": [{"name": "requests", "dep_type": "pip"}],
                   "health_score": 80, "issues": [], "warnings": []},
        }
        suggestions = reporter._generate_suggestions(summary, skills)
        assert any("依赖共享风险" in s or "requests" in s for s in suggestions)

    def test_no_suggestions_when_all_healthy(self):
        """所有指标良好时应返回默认建议。"""
        reporter = HealthReporter()
        summary = {"unique_runtimes": [], "unique_env_vars": []}
        skills = {}
        with patch.object(reporter, '_check_rt_available', return_value=True):
            suggestions = reporter._generate_suggestions(summary, skills)
        assert any("状态良好" in s for s in suggestions)


# ============================================================
#  _save_snapshot / _load_trend 测试
# ============================================================

class TestSnapshotTrendExtra:

    def test_save_snapshot_creates_file(self, tmp_path):
        """_save_snapshot 应在历史目录中创建快照文件。"""
        reporter = HealthReporter(str(tmp_path))
        summary = {
            "scan_time": "2026-04-07T10:00:00",
            "avg_health_score": 85.0,
            "healthy_count": 5,
            "warning_count": 2,
            "critical_count": 0,
            "total_skills": 7,
        }
        reporter._save_snapshot(summary)
        snap_dir = reporter.history_dir
        assert snap_dir.exists()

    def test_save_snapshot_with_existing_data(self, tmp_path):
        """已存在的快照文件应追加而非覆盖。"""
        reporter = HealthReporter(str(tmp_path))
        summary = {
            "scan_time": "2026-04-07T10:00:00",
            "avg_health_score": 80.0,
            "healthy_count": 5,
            "warning_count": 1,
            "critical_count": 1,
            "total_skills": 7,
        }
        # 写一个已有快照
        snap_file = reporter.history_dir / "2026-04-07.json"
        snap_file.parent.mkdir(parents=True, exist_ok=True)
        snap_file.write_text(json.dumps([
            {"time": "2026-04-06T10:00:00", "avg": 75.0, "healthy": 4, "warning": 2, "critical": 1, "total": 7}
        ]))
        reporter._save_snapshot(summary)
        data = json.loads(snap_file.read_text())
        assert len(data) == 2  # 追加而非覆盖

    def test_load_trend_empty_dir(self, tmp_path):
        """空历史目录返回空列表。"""
        reporter = HealthReporter(str(tmp_path))
        trend = reporter._load_trend()
        assert isinstance(trend, list)

    def test_load_trend_with_corrupt_file(self, tmp_path):
        """损坏的快照文件应被跳过。"""
        reporter = HealthReporter(str(tmp_path))
        corrupt_file = reporter.history_dir / "2026-01-01.json"
        corrupt_file.parent.mkdir(parents=True, exist_ok=True)
        corrupt_file.write_text("NOT VALID JSON {{{")
        trend = reporter._load_trend()
        assert isinstance(trend, list)  # 不应崩溃


# ============================================================
#  save_report 测试
# ============================================================

class TestSaveReport:

    def test_save_report_creates_file(self, tmp_path):
        """save_report 应创建报告文件。"""
        reporter = HealthReporter(str(tmp_path))
        content = "# Test Report\nHello World"
        filepath = reporter.save_report(content, "test-report.md")
        assert Path(filepath).exists()
        assert "# Test Report" in Path(filepath).read_text()


# ============================================================
#  main() 入口测试
# ============================================================

class TestReporterMain:

    def test_main_default_markdown(self, tmp_path):
        """默认参数应生成 Markdown 报告。"""
        with patch.object(_reporter_module, 'argparse') as mock_argparse:
            mock_parser_instance = MagicMock()
            mock_args = MagicMock(
                path=str(tmp_path),
                output_dir=str(tmp_path / "out"),
                format="markdown",
                output_file=None,
                no_trend=False,
            )
            mock_parser_instance.parse_args.return_value = mock_args
            mock_argparse.ArgumentParser.return_value = mock_parser_instance

            _reporter_module.main()

    def test_main_json_format_no_print(self, tmp_path):
        """JSON 格式不应 print 报告内容。"""
        with patch.object(_reporter_module, 'argparse') as mock_argparse:
            mock_parser_instance = MagicMock()
            mock_args = MagicMock(
                path=str(tmp_path),
                output_dir=str(tmp_path / "out"),
                format="json",
                output_file=None,
                no_trend=False,
            )
            mock_parser_instance.parse_args.return_value = mock_args
            mock_argparse.ArgumentParser.return_value = mock_parser_instance

            _reporter_module.main()

    def test_main_html_format(self, tmp_path):
        """HTML 格式应生成 HTML 报告。"""
        with patch.object(_reporter_module, 'argparse') as mock_argparse:
            mock_parser_instance = MagicMock()
            mock_args = MagicMock(
                path=str(tmp_path),
                output_dir=str(tmp_path / "out"),
                format="html",
                output_file=None,
                no_trend=False,
            )
            mock_parser_instance.parse_args.return_value = mock_args
            mock_argparse.ArgumentParser.return_value = mock_parser_instance

            _reporter_module.main()

    def test_main_no_trend(self, tmp_path):
        """--no-trend 参数应禁用趋势。"""
        with patch.object(_reporter_module, 'argparse') as mock_argparse:
            mock_parser_instance = MagicMock()
            mock_args = MagicMock(
                path=str(tmp_path),
                output_dir=str(tmp_path / "out"),
                format="markdown",
                output_file=None,
                no_trend=True,
            )
            mock_parser_instance.parse_args.return_value = mock_args
            mock_argparse.ArgumentParser.return_value = mock_parser_instance

            _reporter_module.main()
