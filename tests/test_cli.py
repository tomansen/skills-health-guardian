"""
test_cli.py — CLI 统一命令行入口单元测试
覆盖：colorize, status_icon, score_color_str, format_table, format_quiet,
      format_json_output, format_markdown_output, run_watch_mode, main
"""

import json
import sys
import pytest
from pathlib import Path
from unittest.mock import patch, MagicMock

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "scripts"))

from cli import (
    Colors,
    colorize,
    status_icon,
    score_color_str,
    format_table,
    format_quiet,
    format_json_output,
    format_markdown_output,
    run_watch_mode,
    main,
)
from scanner import SkillsScanner, SkillReport


# ============================================================
#  Fixtures
# ============================================================

@pytest.fixture
def scanner_with_skills(tmp_path):
    """创建含多个 skill 的 scanner 实例。"""
    scanner = SkillsScanner(str(tmp_path))
    scanner.skills = {
        "healthy-skill": SkillReport(
            name="healthy-skill", path=str(tmp_path / "healthy-skill"),
            health_score=95, issues=[], warnings=[],
            dependencies=[], runtime_requirements=[], env_vars=[],
            script_files=[], skill_md_exists=True,
        ),
        "warning-skill": SkillReport(
            name="warning-skill", path=str(tmp_path / "warning-skill"),
            health_score=60, issues=["缺少运行时: bun"],
            warnings=["未设置环境变量: OPENAI_API_KEY"],
            dependencies=[], runtime_requirements=["bun"], env_vars=["OPENAI_API_KEY"],
            script_files=["scripts/main.py"], skill_md_exists=True,
        ),
        "critical-skill": SkillReport(
            name="critical-skill", path=str(tmp_path / "critical-skill"),
            health_score=30, issues=["缺少 SKILL.md 文件", "缺少运行时: uv"],
            warnings=[],
            dependencies=[], runtime_requirements=["uv"], env_vars=[],
            script_files=["scripts/app.py"], skill_md_exists=False,
        ),
    }
    return scanner


@pytest.fixture
def scanner_global_issues(scanner_with_skills):
    """添加全局问题的 scanner。"""
    scanner_with_skills.global_issues = [
        {"type": "version_conflict", "dependency": "requests", "count": 2},
        {"type": "heavy_runtime_dependency", "runtime": "node", "count": 5},
    ]
    return scanner_with_skills


# ============================================================
#  colorize 测试
# ============================================================

class TestColorize:
    """彩色输出工具测试。"""

    def test_colorize_returns_text_when_no_color_env(self, monkeypatch):
        """NO_COLOR 环境变量设置时应返回纯文本。"""
        monkeypatch.setenv("NO_COLOR", "1")
        result = colorize("hello", Colors.GREEN)
        assert result == "hello"

    @patch("cli.sys.stdout.isatty", return_value=False)
    def test_colorize_returns_plain_when_not_tty(self, mock_tty):
        """非 TTY 时返回纯文本。"""
        result = colorize("hello", Colors.GREEN)
        assert result == "hello"

    @patch("cli.sys.stdout.isatty", return_value=True)
    def test_colorize_returns_colored_when_tty(self, mock_tty, monkeypatch):
        """TTY 且无 NO_COLOR 时返回带颜色代码的文本。"""
        monkeypatch.delenv("NO_COLOR", raising=False)
        result = colorize("hello", Colors.GREEN)
        assert Colors.GREEN in result
        assert Colors.END in result
        assert "hello" in result

    @patch("cli.sys.stdout.isatty", return_value=True)
    def test_colorize_all_colors(self, mock_tty, monkeypatch):
        """所有定义的颜色都能正常工作。"""
        monkeypatch.delenv("NO_COLOR", raising=False)
        for color in [Colors.GREEN, Colors.YELLOW, Colors.RED, Colors.BOLD, Colors.CYAN]:
            result = colorize("test", color)
            assert color in result


# ============================================================
#  status_icon 测试
# ============================================================

class TestStatusIcon:

    @patch("cli.colorize", return_value="COLORED")
    def test_healthy_score(self, mock_col):
        """≥80 分应返回 Healthy 状态。"""
        status_icon(85)
        assert "Healthy" in mock_col.call_args[0][0]

    @patch("cli.colorize", return_value="COLORED")
    def test_warning_score(self, mock_col):
        """50-79 分应返回 Warning 状态。"""
        status_icon(60)
        assert "Warning" in mock_col.call_args[0][0]

    @patch("cli.colorize", return_value="COLORED")
    def test_error_score(self, mock_col):
        """<50 分应返回 Error 状态。"""
        status_icon(30)
        assert "Error" in mock_col.call_args[0][0]

    @patch("cli.colorize", return_value="COLORED")
    def test_boundary_80(self, mock_col):
        """80 分边界值应返回 Healthy。"""
        status_icon(80)
        assert "Healthy" in mock_col.call_args[0][0]

    @patch("cli.colorize", return_value="COLORED")
    def test_boundary_50(self, mock_col):
        """50 分边界值应返回 Warning。"""
        status_icon(50)
        assert "Warning" in mock_col.call_args[0][0]


# ============================================================
#  score_color_str 测试
# ============================================================

class TestScoreColorStr:

    @patch("cli.colorize", return_value="COLORED")
    def test_high_score(self, mock_col):
        score_color_str(90)
        assert "90/100" in mock_col.call_args[0][0]

    @patch("cli.colorize", return_value="COLORED")
    def test_mid_score(self, mock_col):
        score_color_str(55)
        assert "55/100" in mock_col.call_args[0][0]

    @patch("cli.colorize", return_value="COLORED")
    def test_low_score(self, mock_col):
        score_color_str(20)
        assert "20/100" in mock_col.call_args[0][0]


# ============================================================
#  format_table 测试
# ============================================================

class TestFormatTable:

    def test_returns_string(self, scanner_with_skills):
        """应返回字符串。"""
        result = format_table(scanner_with_skills)
        assert isinstance(result, str)

    def test_contains_title(self, scanner_with_skills):
        """应包含标题文本。"""
        result = format_table(scanner_with_skills)
        assert "Skills Health Guardian" in result

    def test_contains_skill_names(self, scanner_with_skills):
        """应包含所有 skill 名称。"""
        result = format_table(scanner_with_skills)
        assert "healthy-skill" in result
        assert "warning-skill" in result
        assert "critical-skill" in result

    def test_contains_scores(self, scanner_with_skills):
        """应包含健康分数。"""
        result = format_table(scanner_with_skills)
        assert "95" in result
        assert "60" in result
        assert "30" in result

    def test_contains_box_borders(self, scanner_with_skills):
        """应包含 Unicode 表格边框。"""
        result = format_table(scanner_with_skills)
        assert "╔" in result
        assert "╚" in result
        assert "║" in result

    def test_contains_summary_stats(self, scanner_with_skills):
        """应包含底部统计信息。"""
        result = format_table(scanner_with_skills)
        assert "Total:" in result or "Total" in result

    def test_verbose_shows_issues(self, scanner_with_skills):
        """verbose 模式应显示具体问题。"""
        result = format_table(scanner_with_skills, verbose=True)
        assert "缺少运行时: bun" in result

    def test_non_verbose_hides_issues(self, scanner_with_skills):
        """非 verbose 模式不应显示具体问题。"""
        result = format_table(scanner_with_skills, verbose=False)
        assert "缺少运行时: bun" not in result

    def test_verbose_shows_dependencies(self, tmp_path):
        """verbose 模式应显示依赖信息。"""
        scanner = SkillsScanner(str(tmp_path))
        scanner.skills = {
            "dep-skill": SkillReport(
                name="dep-skill", path=str(tmp_path),
                health_score=90, issues=[], warnings=[],
                dependencies=[
                    MagicMock(name="requests"),
                    MagicMock(name="numpy"),
                ],
                runtime_requirements=[], env_vars=[],
                script_files=["scripts/app.py"], skill_md_exists=True,
            ),
        }
        result = format_table(scanner, verbose=True)
        assert "requests" in result


# ============================================================
#  format_quiet 测试
# ============================================================

class TestFormatQuiet:

    def test_returns_one_line(self, scanner_with_skills):
        """应返回单行摘要。"""
        result = format_quiet(scanner_with_skills)
        lines = result.strip().split("\n")
        assert len(lines) == 1

    def test_contains_score(self, scanner_with_skills):
        """应包含健康分数。"""
        result = format_quiet(scanner_with_skills)
        assert "SHG score=" in result

    def test_contains_counts(self, scanner_with_skills):
        """应包含各状态计数。"""
        result = format_quiet(scanner_with_skills)
        assert "ok=" in result
        assert "warn=" in result
        assert "crit=" in result
        assert "total=" in result


# ============================================================
#  format_json_output 测试
# ============================================================

class TestFormatJsonOutput:

    def test_returns_valid_json(self, scanner_with_skills):
        """应返回合法 JSON。"""
        result = format_json_output(scanner_with_skills)
        data = json.loads(result)
        assert isinstance(data, dict)

    def test_contains_version(self, scanner_with_skills):
        """应包含版本信息。"""
        result = format_json_output(scanner_with_skills)
        data = json.loads(result)
        assert data["version"] == "1.0.0"

    def test_contains_all_skills(self, scanner_with_skills):
        """应包含所有 skill 数据。"""
        result = format_json_output(scanner_with_skills)
        data = json.loads(result)
        assert "healthy-skill" in data["skills"]
        assert "warning-skill" in data["skills"]
        assert "critical-skill" in data["skills"]

    def test_contains_health_scores(self, scanner_with_skills):
        """JSON 中应包含正确的健康分数。"""
        result = format_json_output(scanner_with_skills)
        data = json.loads(result)
        assert data["skills"]["healthy-skill"]["health_score"] == 95
        assert data["skills"]["critical-skill"]["health_score"] == 30

    def test_contains_status_field(self, scanner_with_skills):
        """JSON 中应包含状态字段。"""
        result = format_json_output(scanner_with_skills)
        data = json.loads(result)
        assert data["skills"]["healthy-skill"]["status"] == "healthy"
        assert data["skills"]["warning-skill"]["status"] == "warning"
        assert data["skills"]["critical-skill"]["status"] == "critical"

    def test_includes_global_issues(self, scanner_global_issues):
        """有全局问题时应包含在 JSON 中。"""
        result = format_json_output(scanner_global_issues)
        data = json.loads(result)
        assert "global_issues" in data
        assert len(data["global_issues"]) == 2


# ============================================================
#  format_markdown_output 测试
# ============================================================

class TestFormatMarkdownOutput:

    def test_returns_string(self, scanner_with_skills):
        """应返回字符串。"""
        result = format_markdown_output(scanner_with_skills)
        assert isinstance(result, str)

    def test_contains_markdown_syntax(self, scanner_with_skills):
        """应包含 Markdown 语法。"""
        result = format_markdown_output(scanner_with_skills)
        assert "#" in result  # 标题
        assert "|" in result  # 表格


# ============================================================
#  run_watch_mode 测试
# ============================================================

class TestRunWatchMode:

    def test_watch_mode_with_count(self, scanner_with_skills, tmp_path):
        """watch_count=1 时应只执行一次。"""
        args = MagicMock(
            watch_interval=1,
            watch_count=1,
            path=str(tmp_path),
            skill=None,
            format="json",
            verbose=False,
            output_dir="",
        )
        with patch("cli.time.sleep"), \
             patch("cli.format_json_output", return_value="{}"), \
             patch("cli.sys.stdout.isatty", return_value=False):
            run_watch_mode(args)

    def test_watch_mode_invalid_skill(self, tmp_path):
        """watch 模式中 skill 不存在时应退出。"""
        args = MagicMock(
            watch_interval=1,
            watch_count=0,
            path=str(tmp_path),
            skill="nonexistent",
            format="table",
            verbose=False,
            output_dir="",
        )
        # 注意：patch sys.exit 后，代码会继续执行到 format_table
        # 所以需要同时 mock format_table 避免 scanner 为空导致错误
        with patch("cli.sys.exit") as mock_exit, \
             patch("cli.print"), \
             patch("cli.time.sleep"), \
             patch("cli.format_table", return_value="MOCK TABLE"):
            run_watch_mode(args)
            mock_exit.assert_called_once_with(1)


# ============================================================
#  main 函数测试
# ============================================================

class TestMain:

    @patch("cli.argparse.ArgumentParser.parse_args")
    @patch("cli.format_table", return_value="TABLE OUTPUT")
    @patch("cli.SkillsScanner")
    def test_main_default_table_format(self, mock_scanner_cls, mock_fmt, mock_parse, capsys):
        """默认参数应以 table 格式输出。"""
        scanner_instance = MagicMock()
        scanner_instance.skills = {}
        mock_scanner_cls.return_value = scanner_instance
        mock_parse.return_value = MagicMock(
            watch=None, skill=None, format="table",
            output=None, output_dir="", verbose=False,
            skip_fix=True, dry_run=False, no_color=False,
        )
        main()
        captured = capsys.readouterr()
        assert "TABLE OUTPUT" in captured.out

    @patch("cli.argparse.ArgumentParser.parse_args")
    @patch("cli.format_json_output", return_value='{"test": true}')
    @patch("cli.SkillsScanner")
    def test_main_json_format(self, mock_scanner_cls, mock_fmt, mock_parse, capsys):
        """JSON 格式应输出到 stdout。"""
        scanner_instance = MagicMock()
        scanner_instance.skills = {}
        scanner_instance.get_summary.return_value = {"total_skills": 0}
        mock_scanner_cls.return_value = scanner_instance
        mock_parse.return_value = MagicMock(
            watch=None, skill=None, format="json",
            output=None, output_dir="", verbose=False,
            skip_fix=True, dry_run=False, no_color=False,
        )
        main()
        captured = capsys.readouterr()
        assert '{"test": true}' in captured.out

    @patch("cli.argparse.ArgumentParser.parse_args")
    @patch("cli.format_quiet", return_value="quiet output")
    @patch("cli.SkillsScanner")
    def test_main_quiet_format(self, mock_scanner_cls, mock_fmt, mock_parse, capsys):
        """quiet 格式应输出单行摘要。"""
        scanner_instance = MagicMock()
        scanner_instance.skills = {}
        scanner_instance.get_summary.return_value = {"total_skills": 0}
        mock_scanner_cls.return_value = scanner_instance
        mock_parse.return_value = MagicMock(
            watch=None, skill=None, format="quiet",
            output=None, output_dir="", verbose=False,
            skip_fix=True, dry_run=False, no_color=False,
        )
        main()
        captured = capsys.readouterr()
        assert "quiet output" in captured.out

    @patch("cli.argparse.ArgumentParser.parse_args")
    @patch("cli.format_table", return_value="TABLE")
    @patch("cli.SkillsScanner")
    def test_main_output_to_file(self, mock_scanner_cls, mock_fmt, mock_parse, tmp_path, capsys):
        """指定 -o 时应将输出保存到文件。"""
        scanner_instance = MagicMock()
        scanner_instance.skills = {}
        scanner_instance.get_summary.return_value = {"total_skills": 0}
        mock_scanner_cls.return_value = scanner_instance
        out_file = str(tmp_path / "report.txt")
        mock_parse.return_value = MagicMock(
            watch=None, skill=None, format="table",
            output=out_file, output_dir="", verbose=False,
            skip_fix=True, dry_run=False, no_color=False,
        )
        main()
        assert Path(out_file).exists()
        assert Path(out_file).read_text() == "TABLE"

    @patch("cli.argparse.ArgumentParser.parse_args")
    @patch("cli.run_watch_mode")
    def test_main_watch_mode(self, mock_watch, mock_parse):
        """指定 --watch 时应进入 watch 模式。"""
        mock_parse.return_value = MagicMock(
            watch=30, skill=None, format="table",
            output=None, output_dir="", verbose=False,
            skip_fix=True, dry_run=False, no_color=False,
        )
        main()
        mock_watch.assert_called_once()

    @patch("cli.argparse.ArgumentParser.parse_args")
    @patch("cli.sys.exit")
    @patch("cli.SkillsScanner")
    def test_main_nonexistent_skill(self, mock_scanner_cls, mock_exit, mock_parse, tmp_path):
        """指定不存在的 skill 时应退出。"""
        scanner_instance = MagicMock()
        mock_scanner_cls.return_value = scanner_instance
        mock_parse.return_value = MagicMock(
            watch=None, skill="nonexistent-skill", format="table",
            output=None, output_dir="", verbose=False,
            path=str(tmp_path),
            skip_fix=True, dry_run=False, no_color=False,
        )
        with patch.object(Path, "exists", return_value=False):
            main()
        mock_exit.assert_called_once_with(1)

    @patch("cli.argparse.ArgumentParser.parse_args")
    @patch("cli.os.environ", {})
    def test_main_no_color_flag(self, mock_parse):
        """--no-color 应设置 NO_COLOR 环境变量。"""
        mock_parse.return_value = MagicMock(
            watch=None, skill=None, format="table",
            output=None, output_dir="", verbose=False,
            skip_fix=True, dry_run=False, no_color=True,
        )
        with patch("cli.SkillsScanner"), \
             patch("cli.format_table", return_value=""):
            main()
        import cli
        assert cli.os.environ.get("NO_COLOR") == "1"

    @patch("cli.argparse.ArgumentParser.parse_args")
    @patch("cli.format_table", return_value="TABLE")
    @patch("cli.SkillsScanner")
    def test_main_specific_skill(self, mock_scanner_cls, mock_fmt, mock_parse, tmp_path, capsys):
        """指定 --skill 时应只扫描单个 skill。"""
        scanner_instance = MagicMock()
        scanner_instance.skills = {}
        scanner_instance.get_summary.return_value = {"total_skills": 1}
        mock_scanner_cls.return_value = scanner_instance
        mock_parse.return_value = MagicMock(
            watch=None, skill="my-skill", format="table",
            output=None, output_dir="", verbose=False,
            path=str(tmp_path),
            skip_fix=True, dry_run=False, no_color=False,
        )
        with patch.object(Path, "exists", return_value=True):
            main()
        scanner_instance._scan_single_skill.assert_called_once()


# ============================================================
#  Colors 常量测试
# ============================================================

class TestColors:
    """ANSI 颜色码常量测试。"""

    def test_all_colors_have_values(self):
        """所有颜色常量应有值。"""
        assert Colors.GREEN
        assert Colors.YELLOW
        assert Colors.RED
        assert Colors.BOLD
        assert Colors.DIM
        assert Colors.CYAN
        assert Colors.MAGENTA
        assert Colors.END
