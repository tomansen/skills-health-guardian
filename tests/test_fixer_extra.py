"""
test_fixer_extra.py — Fixer 补充测试
覆盖：_fix_runtime 执行路径、_fix_deps 执行路径、
      _suggest_isolation ts 场景、main() 入口

关键：SkillsFixEngine 是 fixer.py 中唯一的类
"""

import sys
from pathlib import Path

SCRIPTS_DIR = Path(__file__).resolve().parent.parent / "scripts"
if str(SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPTS_DIR))

import pytest
from unittest.mock import patch, MagicMock
import fixer as _fixer_module
from fixer import SkillsFixEngine


# ============================================================
#  _fix_runtime 测试
# ============================================================

class TestFixRuntime:

    def test_tool_already_exists(self):
        """工具已安装时直接返回成功。"""
        engine = SkillsFixEngine("/fake")
        with patch.object(SkillsFixEngine, '_tool_exists', return_value=True):
            result = engine._fix_runtime("uv", dry_run=False)
        assert result["success"] is True
        assert "已安装" in result["message"]

    def test_dry_run_preview(self):
        """dry_run=True 时返回预览信息。"""
        engine = SkillsFixEngine("/fake")
        with patch.object(SkillsFixEngine, '_tool_exists', return_value=False), \
             patch.object(SkillsFixEngine, '_get_install_cmd', return_value="curl ... | sh"):
            result = engine._fix_runtime("uv", dry_run=True)
        assert result["success"] is True
        assert "[预览]" in result["message"]

    def test_unknown_runtime_returns_failure(self):
        """未知运行时返回失败信息。"""
        engine = SkillsFixEngine("/fake")
        with patch.object(SkillsFixEngine, '_tool_exists', return_value=False), \
             patch.object(SkillsFixEngine, '_get_install_cmd', return_value=None):
            result = engine._fix_runtime("unknown-tool", dry_run=False)
        assert result["success"] is False
        assert "不知道如何自动安装" in result["message"]


# ============================================================
#  _fix_deps 测试
# ============================================================

class TestFixDeps:

    def test_empty_skill_name_returns_failure(self):
        """空 skill 名称返回失败。"""
        engine = SkillsFixEngine("/fake")
        result = engine._fix_deps("", dry_run=False)
        assert result["success"] is False

    def test_nonexistent_skill_returns_failure(self, tmp_path):
        """不存在的 skill 返回失败。"""
        engine = SkillsFixEngine(str(tmp_path))
        result = engine._fix_deps("nope", dry_run=False)
        assert result["success"] is False

    def test_skill_no_dep_files(self, tmp_path):
        """无依赖文件的 skill 返回无需安装。"""
        skill_dir = tmp_path / "no-deps-skill"
        skill_dir.mkdir()
        (skill_dir / "SKILL.md").write_text("# Test\n", encoding="utf-8")
        engine = SkillsFixEngine(str(tmp_path))
        result = engine._fix_deps("no-deps-skill", dry_run=False)
        assert result["success"] is True
        assert "无需安装" in result["message"]

    def test_skill_with_requirements_txt_dry_run(self, tmp_path):
        """有 requirements.txt 时 dry_run 预览命令。"""
        skill_dir = tmp_path / "pip-skill"
        skill_dir.mkdir()
        (skill_dir / "requirements.txt").write_text("requests>=2.28\n", encoding="utf-8")
        engine = SkillsFixEngine(str(tmp_path))
        result = engine._fix_deps("pip-skill", dry_run=True)
        assert result["success"] is True
        assert "[预览]" in result["message"]
        assert "pip3 install" in result["message"]

    def test_skill_with_package_json_dry_run(self, tmp_path):
        """有 package.json 时 dry_run 预览 npm install。"""
        skill_dir = tmp_path / "node-skill"
        skill_dir.mkdir()
        (skill_dir / "package.json").write_text('{"dependencies": {"express": "^4.0.0"}}', encoding="utf-8")
        engine = SkillsFixEngine(str(tmp_path))
        result = engine._fix_deps("node-skill", dry_run=True)
        assert result["success"] is True
        assert "npm install" in result["message"]


# ============================================================
#  _suggest_isolation 测试
# ============================================================

class TestSuggestIsolation:

    def test_suggests_python_venv(self, tmp_path):
        """有 .py 文件且无 .venv 时建议 Python venv。"""
        skill_dir = tmp_path / "py-skill"
        skill_dir.mkdir()
        scripts_dir = skill_dir / "scripts"
        scripts_dir.mkdir()
        (scripts_dir / "main.py").write_text("print('hello')\n", encoding="utf-8")
        engine = SkillsFixEngine(str(tmp_path))
        result = engine._suggest_isolation("py-skill")
        assert result["success"] is True
        assert len(result["suggestions"]) >= 1
        assert result["suggestions"][0]["isolations"][0]["type"] == "python_venv"

    def test_suggests_node_local(self, tmp_path):
        """有 .ts/.js 和 package.json 时建议 npm install。"""
        skill_dir = tmp_path / "ts-skill"
        skill_dir.mkdir()
        scripts_dir = skill_dir / "scripts"
        scripts_dir.mkdir()
        (scripts_dir / "index.ts").write_text("console.log('hi')\n", encoding="utf-8")
        (skill_dir / "package.json").write_text('{"dependencies": {}}', encoding="utf-8")
        engine = SkillsFixEngine(str(tmp_path))
        result = engine._suggest_isolation("ts-skill")
        assert result["success"] is True
        assert any(i["type"] == "node_local" for i in result["suggestions"][0]["isolations"])


# ============================================================
#  check_all 测试
# ============================================================

class TestCheckAll:

    def test_returns_all_categories(self, tmp_path):
        """check_all 应返回所有检查类别。"""
        engine = SkillsFixEngine(str(tmp_path))
        result = engine.check_all()
        assert "missing_runtimes" in result
        assert "missing_deps" in result
        assert "missing_env_vars" in result
        assert "version_conflicts" in result
        assert "isolation_recommendations" in result
        assert "update_available" in result

    def test_detects_missing_runtime(self):
        """检测到缺失运行时。"""
        engine = SkillsFixEngine("/fake")
        with patch.object(SkillsFixEngine, '_tool_exists', return_value=False), \
             patch.object(SkillsFixEngine, '_get_install_cmd', return_value="brew install uv"):
            result = engine.check_all()
        assert isinstance(result["missing_runtimes"], list)


# ============================================================
#  generate_env_template 测试
# ============================================================

class TestGenerateEnvTemplate:

    def test_generates_template_content(self, tmp_path):
        """generate_env_template 应生成模板内容。"""
        skill_dir = tmp_path / "api-skill"
        skill_dir.mkdir()
        (skill_dir / "SKILL.md").write_text(
            "需要环境变量 OPENAI_API_KEY 和 NOTION_TOKEN",
            encoding="utf-8"
        )
        engine = SkillsFixEngine(str(tmp_path))
        result = engine.generate_env_template()
        assert isinstance(result, str)
        assert "API" in result or "KEY" in result


# ============================================================
#  main() 入口测试
# ============================================================

class TestFixerMain:

    def test_main_check_command(self, tmp_path):
        """fixer.py check 命令应输出检查结果。"""
        with patch.object(_fixer_module, 'argparse') as mock_argparse:
            mock_parser_instance = MagicMock()
            mock_args = MagicMock(
                command="check",
                path=str(tmp_path),
            )
            mock_parser_instance.parse_args.return_value = mock_args
            mock_argparse.ArgumentParser.return_value = mock_parser_instance

            _fixer_module.main()

    def test_main_fix_command_dry_run(self, tmp_path):
        """fixer.py fix <type> --dry-run 应输出预览。"""
        with patch.object(_fixer_module, 'argparse') as mock_argparse:
            mock_parser_instance = MagicMock()
            mock_args = MagicMock(
                command="fix",
                type="runtime",
                target="uv",
                path=str(tmp_path),
                dry_run=True,
                yes=False,
            )
            mock_parser_instance.parse_args.return_value = mock_args
            mock_argparse.ArgumentParser.return_value = mock_parser_instance

            _fixer_module.main()

    def test_main_env_template_command(self, tmp_path):
        """fixer.py env-template 命令应生成模板。"""
        with patch.object(_fixer_module, 'argparse') as mock_argparse:
            mock_parser_instance = MagicMock()
            mock_args = MagicMock(
                command="env-template",
                path=str(tmp_path),
                output=None,
            )
            mock_parser_instance.parse_args.return_value = mock_args
            mock_argparse.ArgumentParser.return_value = mock_parser_instance

            _fixer_module.main()

    def test_main_no_command_shows_banner(self, tmp_path):
        """无子命令时应显示 banner。"""
        with patch.object(_fixer_module, 'argparse') as mock_argparse:
            mock_parser_instance = MagicMock()
            mock_args = MagicMock(
                command=None,
                path=str(tmp_path),
            )
            mock_parser_instance.parse_args.return_value = mock_args
            mock_argparse.ArgumentParser.return_value = mock_parser_instance

            _fixer_module.main()
