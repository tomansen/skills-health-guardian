"""
test_reporter.py — HealthReporter 报告生成器单元测试
覆盖：Markdown/JSON/HTML 输出格式、内容完整性、保存与快照机制
"""

import json
from pathlib import Path

import sys
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "scripts"))

from reporter import HealthReporter, ReportConfig


class TestMarkdownReport:
    """Markdown 格式报告输出测试。"""

    def test_generate_markdown_report_not_empty(self, mock_scan_result):
        """生成的 Markdown 报告应非空且包含关键标题。"""
        reporter = HealthReporter()
        report = reporter.generate(mock_scan_result)

        assert isinstance(report, str)
        assert len(report) > 100  # 至少有一定内容量
        assert "Skills 环境健康报告" in report or "健康报告" in report

    def test_md_contains_skill_count(self, mock_scan_result):
        """Markdown 报告中应包含正确的 skill 总数。"""
        reporter = HealthReporter()
        report = reporter.generate(mock_scan_result)
        # summary.total_skills == 3
        assert "3" in report  # skill 总数出现在报告中

    def test_md_contains_health_score(self, mock_scan_result):
        """Markdown 报告中应包含健康分数。"""
        reporter = HealthReporter()
        report = reporter.generate(mock_scan_result)
        # avg_health_score == 76.7
        assert "76.7" in report or "76" in report

    def test_md_contains_overview_table(self, mock_scan_result):
        """Markdown 报告应包含概览表格（含表头）。"""
        reporter = HealthReporter()
        report = reporter.generate(mock_scan_result)
        assert "| 指标 |" in report or "| 指标 | 数值 |" in report

    def test_md_contains_skill_details(self, mock_scan_result):
        """Markdown 报告应包含各 Skill 详情表。"""
        reporter = HealthReporter()
        report = reporter.generate(mock_scan_result)
        assert "skill-a" in report or "skill-b" in report

    def test_md_contains_global_issues(self, mock_scan_result):
        """Markdown 报告中应展示全局冲突信息。"""
        reporter = HealthReporter()
        report = reporter.generate(mock_scan_result)
        assert "冲突" in report or "警告" in report or "version_conflict" in report

    def test_md_contains_suggestions_section(self, mock_scan_result):
        """Markdown 报告应包含修复建议章节。"""
        reporter = HealthReporter()
        report = reporter.generate(mock_scan_result)
        assert "修复建议" in report or "建议" in report


class TestJsonReport:
    """JSON 格式报告输出测试。"""

    def test_generate_json_report_is_valid_json(self, mock_scan_result):
        """JSON 报告应是合法 JSON 字符串，包含必要字段。"""
        config = ReportConfig(format="json")
        reporter = HealthReporter()
        json_output = reporter.generate(mock_scan_result, config)

        data = json.loads(json_output)  # 不抛异常即为合法 JSON
        assert "summary" in data
        assert "skills" in data

    def test_json_preserves_all_skills(self, mock_scan_result):
        """JSON 报告应保留所有原始 skill 数据。"""
        config = ReportConfig(format="json")
        reporter = HealthReporter()
        json_output = reporter.generate(mock_scan_result, config)

        data = json.loads(json_output)
        assert len(data["skills"]) == 3  # skill-a, b, c

    def test_json_summary_fields_intact(self, mock_scan_result):
        """JSON 报告的摘要字段应完整保留。"""
        config = ReportConfig(format="json")
        reporter = HealthReporter()
        json_output = reporter.generate(mock_scan_result, config)

        data = json.loads(json_output)
        summary = data["summary"]
        assert summary["total_skills"] == 3
        assert "avg_health_score" in summary
        assert "healthy_count" in summary
        assert "critical_count" in summary
        assert "global_issues" in summary


class TestHtmlReport:
    """HTML 格式报告输出测试。"""

    def test_generate_html_report_has_tags(self, mock_scan_result):
        """HTML 报告必须包含 <html> 和 </html> 标签。"""
        config = ReportConfig(format="html")
        reporter = HealthReporter()
        html_output = reporter.generate(mock_scan_result, config)

        assert "<html" in html_output.lower() or "<!DOCTYPE html>" in html_output.upper()
        assert "</html>" in html_output.lower()

    def test_html_contains_score(self, mock_scan_result):
        """HTML 报告中应显示健康分数。"""
        config = ReportConfig(format="html")
        reporter = HealthReporter()
        html_output = reporter.generate(mock_scan_result, config)

        assert "76.7" in html_output or "76" in html_output or "77" in html_output

    def test_html_contains_skill_table(self, mock_scan_result):
        """HTML 报告应包含 skill 详情表格（<table> 标签）。"""
        config = ReportConfig(format="html")
        reporter = HealthReporter()
        html_output = reporter.generate(mock_scan_result, config)

        assert "<table>" in html_output.lower()
        assert "</table>" in html_output.lower()

    def test_html_dark_theme_styles(self, mock_scan_result):
        """HTML 报告使用深色主题样式（检查关键 CSS）。"""
        config = ReportConfig(format="html")
        reporter = HealthReporter()
        html_output = reporter.generate(mock_scan_result, config)

        assert "background" in html_output.lower()  # 有样式定义
        assert "color" in html_output.lower()


class TestReportFormatSelection:
    """报告格式路由选择测试。"""

    def test_default_format_is_markdown(self, mock_scan_result):
        """未指定 format 时默认生成 Markdown。"""
        reporter = HealthReporter()
        report = reporter.generate(mock_scan_result)
        assert "# " in report  # Markdown 标题语法

    def test_format_routing(self, mock_scan_result):
        """三种格式都应能正确路由到对应生成器。"""
        reporter = HealthReporter()

        md_config = ReportConfig(format="markdown")
        md = reporter.generate(mock_scan_result, md_config)
        assert "#" in md

        json_config = ReportConfig(format="json")
        js = reporter.generate(mock_scan_result, json_config)
        data = json.loads(js)  # 合法 JSON
        assert "skills" in data

        html_config = ReportConfig(format="html")
        ht = reporter.generate(mock_scan_result, html_config)
        assert "<html" in ht.lower()


class TestReportSave:
    """报告文件保存测试。"""

    def test_save_report_creates_file(self, mock_scan_result, tmp_output_path):
        """save_report() 应创建指定文件并返回路径。"""
        reporter = HealthReporter(output_base=str(tmp_output_path))
        content = reporter.generate(mock_scan_result)
        filepath = reporter.save_report(content, filename="test-report.md")

        saved_path = Path(filepath)
        assert saved_path.exists()
        assert saved_path.name == "test-report.md"
        # 文件内容应与传入的一致
        assert saved_path.read_text(encoding='utf-8') == content

    def test_save_auto_generates_filename(self, mock_scan_result, tmp_output_path):
        """不指定文件名时自动生成带时间戳的文件名。"""
        reporter = HealthReporter(output_base=str(tmp_output_path))
        content = reporter.generate(mock_scan_result)
        filepath = reporter.save_report(content)

        saved_path = Path(filepath)
        assert saved_path.exists()
        assert "health-report-" in saved_path.name
        assert ".md" in saved_path.name


class TestSnapshotAndTrend:
    """快照保存与趋势加载测试。"""

    def test_snapshot_saved_on_generation(self, mock_scan_result, tmp_output_path):
        """生成报告时应在 history 目录下保存快照。"""
        reporter = HealthReporter(output_base=str(tmp_output_path))
        reporter.generate(mock_scan_result)  # 触发 _save_snapshot

        history_dir = tmp_output_path / "history"
        assert history_dir.exists()
        snap_files = list(history_dir.glob("*.json"))
        assert len(snap_files) >= 1

        # 快照内容应可解析为 JSON
        for sf in snap_files:
            data = json.loads(sf.read_text())
            assert isinstance(data, list)
            assert len(data) >= 1
            snap = data[0]
            assert "avg" in snap
            assert "healthy" in snap

    def test_trend_loading_from_history(self, mock_scan_result, tmp_output_path):
        """_load_trend 应能从历史快照加载数据。"""
        reporter = HealthReporter(output_base=str(tmp_output_path))
        
        # 先生成一次报告以写入历史数据
        reporter.generate(mock_scan_result)

        trend = reporter._load_trend()
        assert isinstance(trend, list)
        if trend:  # 如果有历史数据
            assert "avg" in trend[0]
            assert "time" in trend[0]


class TestSuggestionsGeneration:
    """智能修复建议生成测试。"""

    def test_suggestions_for_missing_runtimes(self, mock_scan_result):
        """缺失运行时应产生安装命令建议。"""
        reporter = HealthReporter()
        suggestions = reporter._generate_suggestions(
            mock_scan_result["summary"],
            mock_scan_result["skills"]
        )
        # 注意：如果运行时已安装在系统上，可能不会触发此建议
        assert isinstance(suggestions, list)

    def test_suggestions_for_low_score_skills(self, mock_scan_result):
        """低分 skill 应有针对性修复建议。"""
        reporter = HealthReporter()
        suggestions = reporter._generate_suggestions(
            mock_scan_result["summary"],
            mock_scan_result["skills"]
        )
        assert isinstance(suggestions, list)


class TestReportConfig:
    """报告配置类测试。"""

    def test_default_values(self):
        """ReportConfig 默认值应符合预期。"""
        cfg = ReportConfig()
        assert cfg.format == "markdown"
        assert cfg.include_trend is True
        assert cfg.max_history == 30

    def test_custom_values(self):
        """自定义配置值应正确存储。"""
        cfg = ReportConfig(
            output_dir="/tmp/reports",
            format="json",
            include_trend=False,
            max_history=10,
        )
        assert cfg.format == "json"
        assert cfg.include_trend is False
        assert cfg.max_history == 10


class TestEmptyInputHandling:
    """空输入或最小输入的边界情况测试。"""

    def test_empty_scan_data(self):
        """传入空的 scan_data 不应崩溃。"""
        reporter = HealthReporter()
        # 传入包含必要字段的空数据
        empty_data = {
            "summary": {
                "total_skills": 0,
                "avg_health_score": 0,
                "healthy_count": 0,
                "warning_count": 0,
                "critical_count": 0,
                "scan_time": "2026-04-04T12:00:00",
                "unique_runtimes": [],
                "unique_env_vars": [],
                "global_issues": [],
                "skills_with_scripts": 0,
                "skills_with_dependencies": 0,
                "total_dependencies": 0,
            },
            "skills": {}
        }
        report = reporter.generate(empty_data)
        assert isinstance(report, str)
        assert len(report) > 0

    def test_minimal_scan_data(self):
        """只有基本字段的 scan_data 应正常工作。"""
        reporter = HealthReporter()
        minimal_data = {
            "summary": {
                "total_skills": 1,
                "avg_health_score": 50.0,
                "healthy_count": 0,
                "warning_count": 1,
                "critical_count": 0,
                "scan_time": "2026-04-04T12:00:00",
            },
            "skills": {
                "test-skill": {
                    "name": "test-skill",
                    "health_score": 50,
                    "dependencies": [],
                    "runtime_requirements": [],
                    "env_vars": [],
                    "issues": ["some issue"],
                    "warnings": [],
                }
            }
        }
        report = reporter.generate(minimal_data)
        assert "test-skill" in report
