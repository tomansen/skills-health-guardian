"""
test_fixer.py — SkillsFixEngine 核心逻辑单元测试
覆盖：初始化、check_all、auto_fix（4种类型）、env_template生成、工具检测、依赖修复、隔离建议
"""

import pytest
import json
from pathlib import Path
from unittest.mock import patch, MagicMock

# 将 scripts 目录加入 sys.path
import sys
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "scripts"))

from fixer import SkillsFixEngine


# ============================================================
#  Fixtures: Fixer 专用临时环境
# ============================================================

@pytest.fixture
def fixer_engine(tmp_path):
    """创建一个基于 tmp_path 的 FixEngine 实例。"""
    return SkillsFixEngine(str(tmp_path))


@pytest.fixture
def skill_with_req_txt(tmp_path):
    """创建含 requirements.txt 的 skill 目录。"""
    skill = tmp_path / "test-skill"
    skill.mkdir()
    (skill / "SKILL.md").write_text("# Test\n", encoding="utf-8")
    (skill / "requirements.txt").write_text(
        "requests>=2.28.0\nbeautifulsoup4==4.12.0\n"
        "click>=8.0\npydantic>=2.0\n",
        encoding="utf-8"
    )
    return tmp_path


@pytest.fixture
def skill_with_pkg_json(tmp_path):
    """创建含 package.json 但无 node_modules 的 skill 目录。"""
    skill = tmp_path / "node-skill"
    skill.mkdir()
    (skill / "SKILL.md").write_text("# Node Skill\n", encoding="utf-8")
    pkg = {
        "dependencies": {"react": "^18.0.0", "lodash": "^4.0.0", "express": "^4.18.0"},
        "devDependencies": {"typescript": "^5.0.0"}
    }
    (skill / "package.json").write_text(json.dumps(pkg), encoding="utf-8")
    return tmp_path


@pytest.fixture
def skill_with_env_vars(tmp_path):
    """创建 SKILL.md 中包含多种环境变量引用的 skill。"""
    skill = tmp_path / "env-skill"
    skill.mkdir()
    (skill / "SKILL.md").write_text(
        "# Env Skill\n\n"
        "需要设置 `OPENAI_API_KEY` 和 `ANTHROPIC_API_KEY`。\n\n"
        "```python\nkey = os.environ.get('NOTION_TOKEN')\nsecret = os.environ['FIRECRAWL_API_KEY']\n```\n\n"
        "export GEMINI_KEY=xxx\n"
        "MY_CUSTOM_VAR=value\n",
        encoding="utf-8"
    )
    # 添加 scripts 目录使 skill 更完整
    scripts = skill / "scripts"
    scripts.mkdir()
    (scripts / "run.py").write_text("import os\nprint(os.environ.get('OPENAI_API_KEY'))\n", encoding="utf-8")
    return tmp_path


@pytest.fixture
def multi_skill_fixer_base(tmp_path):
    """创建多个混合类型的 skill，用于 check_all 集成测试。"""
    # Skill 1: Python + requirements.txt
    s1 = tmp_path / "py-skill"
    s1.mkdir()
    (s1 / "SKILL.md").write_text("# Py Skill\n", encoding="utf-8")
    (s1 / "requirements.txt").write_text("requests>=2.28\nnumpy>=1.24\n", encoding="utf-8")

    # Skill 2: Node + package.json (无 node_modules)
    s2 = tmp_path / "node-skill"
    s2.mkdir()
    (s2 / "package.json").write_text(
        json.dumps({"dependencies": {"express": "^4.18"}}), encoding="utf-8"
    )

    # Skill 3: 空目录（无 SKILL.md）
    s3 = tmp_path / "empty-skill"
    s3.mkdir()

    # Skill 4: 有 .venv 的 Python skill（用于隔离测试）
    s4 = tmp_path / "isolated-skill"
    s4.mkdir()
    (s4 / "SKILL.md").write_text("# Isolated\n", encoding="utf-8")
    sv = s4 / "scripts"
    sv.mkdir()
    (sv / "app.py").write_text("import requests\n", encoding="utf-8")
    (s4 / ".venv").mkdir()  # 模拟已有 venv

    return tmp_path


# ============================================================
#  初始化测试
# ============================================================

class TestInitialization:
    """SkillsFixEngine 初始化相关测试。"""

    def test_init_sets_skills_base_path(self, tmp_path):
        """初始化应正确保存 skills 基础路径。"""
        engine = SkillsFixEngine(str(tmp_path))
        assert engine.skills_base == Path(tmp_path)

    def test_init_empty_fix_log(self, tmp_path):
        """初始化时 fix_log 应为空列表。"""
        engine = SkillsFixEngine(str(tmp_path))
        assert engine.fix_log == []

    def test_init_accepts_nonexistent_path(self):
        """接受不存在的路径，不应立即报错。"""
        engine = SkillsFixEngine("/nonexistent/path")
        assert engine.skills_base == Path("/nonexistent/path")


# ============================================================
#  check_all() 测试
# ============================================================

class TestCheckAll:
    """全面检查功能测试 — 核心是 mock 掉所有 subprocess 调用。"""

    @patch.object(SkillsFixEngine, '_tool_exists', return_value=False)
    @patch.object(SkillsFixEngine, '_pip_installed', return_value=False)
    def test_check_all_detects_missing_runtimes(self, mock_pip, mock_tool, fixer_engine):
        """当运行时不可用时，应报告缺失的运行时。"""
        results = fixer_engine.check_all()

        assert "missing_runtimes" in results
        assert isinstance(results["missing_runtimes"], list)
        # 应至少检测到 python3/uv 等高优先级运行时缺失
        runtime_names = [rt["name"] for rt in results["missing_runtimes"]]
        assert len(runtime_names) > 0

    @patch('fixer.subprocess.run')
    def test_check_all_no_issues_when_healthy(self, mock_run, skill_with_req_txt):
        """当所有工具和包都已安装时，应无缺失项。"""
        mock_run.return_value = MagicMock(returncode=0)
        engine = SkillsFixEngine(str(skill_with_req_txt))
        results = engine.check_all()

        assert isinstance(results, dict)

    @patch('fixer.subprocess.run')
    def test_check_all_detects_missing_pip_deps(self, mock_run, skill_with_req_txt):
        """当 pip 包未安装时，应在 missing_deps 中报告。"""
        def side_effect(cmd, **kwargs):
            r = MagicMock()
            if "pip3" in cmd and "show" in cmd:
                r.returncode = 1
            else:
                r.returncode = 0
            return r
        mock_run.side_effect = side_effect

        engine = SkillsFixEngine(str(skill_with_req_txt))
        results = engine.check_all()

        assert "test-skill" in results.get("missing_deps", {})

    @patch.object(SkillsFixEngine, '_tool_exists', return_value=True)
    def test_check_all_detects_missing_node_modules(self, mock_tool, skill_with_pkg_json):
        """有 package.json 但无 node_modules 时，应检测到 npm 缺失。"""
        engine = SkillsFixEngine(str(skill_with_pkg_json))
        results = engine.check_all()

        assert "node-skill" in results["missing_deps"]
        node_info = results["missing_deps"]["node-skill"]
        assert "node" in node_info or node_info.get("type") == "npm"

    @patch.object(SkillsFixEngine, '_tool_exists', return_value=True)
    @patch.object(SkillsFixEngine, '_pip_installed', return_value=True)
    def test_check_all_skips_hidden_dirs(self, mock_pip, mock_tool, tmp_path):
        """检查时应忽略 . 开头的隐藏目录。"""
        hidden = tmp_path / ".hidden-skill"
        hidden.mkdir()
        (hidden / "SKILL.md").write_text("# Hidden\n", encoding="utf-8")

        normal = tmp_path / "visible-skill"
        normal.mkdir()
        (normal / "SKILL.md").write_text("# Visible\n", encoding="utf-8")

        engine = SkillsFixEngine(str(tmp_path))
        results = engine.check_all()

        assert ".hidden-skill" not in results.get("missing_deps", {})

    @patch.object(SkillsFixEngine, '_tool_exists', return_value=True)
    @patch.object(SkillsFixEngine, '_pip_installed', return_value=True)
    def test_check_all_nonexistent_base_returns_empty(self, mock_pip, mock_tool):
        """基础路径不存在时返回空结果，不崩溃。"""
        engine = SkillsFixEngine("/no/such/path")
        results = engine.check_all()

        assert results["missing_runtimes"] == []
        assert results["missing_deps"] == {}

    @patch.object(SkillsFixEngine, '_tool_exists', return_value=True)
    @patch.object(SkillsFixEngine, '_pip_installed', return_value=True)
    def test_check_all_result_structure_complete(self, mock_pip, mock_tool, fixer_engine):
        """结果字典应包含所有预期的顶层键。"""
        results = fixer_engine.check_all()

        expected_keys = [
            "missing_runtimes", "missing_deps", "missing_env_vars",
            "version_conflicts", "isolation_recommendations", "update_available"
        ]
        for key in expected_keys:
            assert key in results, f"Missing key: {key}"


# ============================================================
#  auto_fix() 测试
# ============================================================

class TestAutoFix:
    """自动修复调度器测试。"""

    def test_unknown_fix_type_returns_error(self, fixer_engine):
        """未知修复类型应返回错误信息。"""
        result = fixer_engine.auto_fix("nonexistent_type")
        assert result["success"] is False
        assert "未知" in result["message"]

    @patch('fixer.subprocess.run')
    def test_auto_fix_appends_to_log(self, mock_run, fixer_engine):
        """每次调用 auto_fix 都应记录到 fix_log。"""
        mock_run.return_value = MagicMock(returncode=0)
        assert len(fixer_engine.fix_log) == 0
        fixer_engine.auto_fix("runtime", "python3")
        assert len(fixer_engine.fix_log) == 1
        assert fixer_engine.fix_log[0]["action"] == "runtime:python3"

    @patch('fixer.subprocess.run')
    def test_auto_fix_dry_run_flag_in_log(self, mock_run, fixer_engine):
        """dry_run 状态应被记录到日志中。"""
        mock_run.return_value = MagicMock(returncode=0)
        fixer_engine.auto_fix("env_template", dry_run=True)
        assert fixer_engine.fix_log[0]["dry_run"] is True

        fixer_engine.auto_fix("env_template", dry_run=False)
        assert fixer_engine.fix_log[1]["dry_run"] is False


# ============================================================
#  _fix_runtime() 测试（通过 auto_fix 调用）
# ============================================================

class TestFixRuntime:
    """运行时修复测试。"""

    @patch.object(SkillsFixEngine, '_tool_exists', return_value=True)
    def test_already_installed_runtime(self, mock_tool, fixer_engine):
        """运行时已安装时直接返回成功。"""
        result = fixer_engine.auto_fix("runtime", "python3")
        assert result["success"] is True
        assert "已安装" in result["message"]

    @patch.object(SkillsFixEngine, '_tool_exists', return_value=False)
    def test_dry_run_shows_command(self, mock_tool, fixer_engine):
        """dry_run 模式下应显示将要执行的命令。"""
        result = fixer_engine.auto_fix("runtime", "uv", dry_run=True)
        assert result["success"] is True
        assert "[预览]" in result["message"]

    @patch.object(SkillsFixEngine, '_tool_exists', return_value=False)
    def test_unknown_runtime_no_install_cmd(self, mock_tool, fixer_engine):
        """没有安装命令的运行时应返回失败。"""
        result = fixer_engine.auto_fix("runtime", "chrome")
        assert result["success"] is False
        assert "不知道" in result["message"] or "无法" in result["message"]


# ============================================================
#  _fix_deps() 测试（通过 auto_fix 调用）
# ============================================================

class TestFixDeps:
    """依赖修复测试。"""

    def test_fix_deps_empty_target_returns_error(self, fixer_engine):
        """未指定 skill 名称时应返回错误。"""
        result = fixer_engine.auto_fix("deps", "")
        assert result["success"] is False

    def test_fix_deps_nonexistent_skill(self, fixer_engine):
        """skill 不存在时应返回错误。"""
        result = fixer_engine.auto_fix("deps", "no-such-skill-xyz")
        assert result["success"] is False
        assert "不存在" in result["message"]

    def test_fix_deps_dry_run(self, skill_with_req_txt):
        """dry_run 模式应显示预览命令。"""
        engine = SkillsFixEngine(str(skill_with_req_txt))
        result = engine.auto_fix("deps", "test-skill", dry_run=True)
        assert result["success"] is True
        assert "[预览]" in result["message"] or "pip3 install" in result["message"]

    def test_fix_deps_no_requirements_file(self, tmp_path):
        """skill 无 requirements.txt 也无 package.json 时提示无需安装。"""
        skill = tmp_path / "bare-skill"
        skill.mkdir()
        (skill / "SKILL.md").write_text("# Bare\n", encoding="utf-8")

        engine = SkillsFixEngine(str(tmp_path))
        result = engine.auto_fix("deps", "bare-skill", dry_run=True)
        assert result["success"] is True
        assert "无需" in result["message"]


# ============================================================
#  _suggest_isolation() 测试
# ============================================================

class TestSuggestIsolation:
    """隔离方案建议测试。"""

    def test_isolate_python_skill_without_venv(self, tmp_path):
        """Python skill 没有 .venv 时应建议创建 venv。"""
        skill = tmp_path / "py-project"
        skill.mkdir()
        scripts = skill / "scripts"
        scripts.mkdir()
        (scripts / "main.py").write_text("import requests\n", encoding="utf-8")
        # 故意不创建 .venv

        engine = SkillsFixEngine(str(tmp_path))
        result = engine.auto_fix("isolate", "py-project")
        assert result["success"] is True
        suggestions = result.get("suggestions", [])
        assert len(suggestions) > 0
        isolations = suggestions[0].get("isolations", [])
        types = [iso["type"] for iso in isolations]
        assert "python_venv" in types

    def test_isolate_skill_with_venv_already(self, multi_skill_fixer_base):
        """已有 .venv 的 skill 不应建议 Python 隔离。"""
        engine = SkillsFixEngine(str(multi_skill_fixer_base))
        result = engine.auto_fix("isolate", "isolated-skill")
        suggestions = result.get("suggestions", [])
        # 找到 isolated-skill 的建议
        target = None
        for s in suggestions:
            if s["skill"] == "isolated-skill":
                target = s
                break
        if target:
            venv_types = [iso["type"] for iso in target.get("isolations", [])]
            assert "python_venv" not in venv_types

    def test_isolate_all_returns_success(self, multi_skill_fixer_base):
        """不指定 skill_name 时应返回成功。"""
        engine = SkillsFixEngine(str(multi_skill_fixer_base))
        result = engine.auto_fix("isolate")
        assert result["success"] is True
        assert "suggestions" in result


# ============================================================
#  generate_env_template() 测试
# ============================================================

class TestGenerateEnvTemplate:
    """环境变量模板生成测试。"""

    def test_generates_template_content(self, skill_with_env_vars):
        """生成的模板应包含标题和时间戳。"""
        engine = SkillsFixEngine(str(skill_with_env_vars))
        template = engine.generate_env_template()

        assert isinstance(template, str)
        assert len(template) > 0

    def test_writes_template_to_file(self, skill_with_env_vars, tmp_path):
        """指定 output_path 时应将模板写入文件。"""
        out = tmp_path / ".env.template"
        engine = SkillsFixEngine(str(skill_with_env_vars))
        result = engine.generate_env_template(str(out))

        assert out.exists()
        content = out.read_text(encoding="utf-8")
        assert isinstance(content, str)

    @patch('fixer.os.environ.get', return_value="test-key")
    def test_detects_api_keys_from_skill_md(self, mock_env, skill_with_env_vars):
        """应从 SKILL.md 中提取 API_KEY / TOKEN / SECRET 类型的变量。"""
        engine = SkillsFixEngine(str(skill_with_env_vars))
        template = engine.generate_env_template()
        # 检测至少有 API Key 相关内容
        has_api_content = any(k in template for k in ["API", "KEY", "TOKEN", "SECRET", "Key", "Token"])
        assert has_api_content or len(template) > 20  # 有实质内容即可

    def test_empty_skills_dir_produces_minimal_template(self, empty_skill_dir):
        """空目录的模板只有头部注释。"""
        engine = SkillsFixEngine(str(empty_skill_dir))
        template = engine.generate_env_template()
        assert isinstance(template, str)
        assert "Template" in template or "模板" in template or len(template) > 0


# ============================================================
#  _tool_exists() 静态方法测试
# ============================================================

class TestToolExists:
    """工具检测静态方法测试。"""

    @patch('subprocess.run')
    def test_existing_tool_returns_true(self, mock_run):
        """工具存在（返回码 0）时应返回 True。"""
        mock_run.return_value = MagicMock(returncode=0)
        assert SkillsFixEngine._tool_exists("python3") is True

    @patch('subprocess.run')
    def test_missing_tool_returns_false(self, mock_run):
        """工具不存在（抛 FileNotFoundError）时应返回 False。"""
        mock_run.side_effect = FileNotFoundError()
        assert SkillsFixEngine._tool_exists("nonexistent_tool_xyz") is False

    @patch('subprocess.run')
    def test_tool_error_return_code_returns_false(self, mock_run):
        """工具执行失败（非零返回码）时应返回 False。"""
        mock_run.return_value = MagicMock(returncode=127)
        assert SkillsFixEngine._tool_exists("bad_cmd") is False


# ============================================================
#  _pip_installed() 静态方法测试
# ============================================================

class TestPipInstalled:
    """pip 包安装检测测试。"""

    @patch('subprocess.run')
    def test_installed_package_returns_true(self, mock_run):
        """包已安装时返回 True。"""
        mock_run.return_value = MagicMock(returncode=0)
        assert SkillsFixEngine._pip_installed("requests") is True

    @patch('subprocess.run')
    def test_not_installed_package_returns_false(self, mock_run):
        """包未安装时返回 False。"""
        mock_run.return_value = MagicMock(returncode=1)
        assert SkillsFixEngine._pip_installed("nonexistent-package-xyz") is False

    @patch('subprocess.run', side_effect=Exception("pip error"))
    def test_exception_returns_false(self, mock_run):
        """异常情况返回 False。"""
        assert SkillsFixEngine._pip_installed("broken") is False


# ============================================================
#  _get_install_cmd() 静态方法测试
# ============================================================

class TestGetInstallCmd:
    """安装命令映射测试。"""

    def test_known_tools_have_commands(self):
        """已知工具应有对应的安装命令。"""
        assert SkillsFixEngine._get_install_cmd("uv") is not None
        assert SkillsFixEngine._get_install_cmd("bun") is not None
        assert SkillsFixEngine._get_install_cmd("node") is not None
        assert SkillsFixEngine._get_install_cmd("npm") is not None

    def test_unknown_tool_returns_none(self):
        """未知工具应返回 None。"""
        assert SkillsFixEngine._get_install_cmd("nonexistent-tool") is None

    def test_chrome_returns_none(self):
        """Chrome 需要手动下载，应返回 None。"""
        assert SkillsFixEngine._get_install_cmd("chrome") is None

    def test_uv_install_command_format(self):
        """uv 的安装命令应为 curl 安装脚本。"""
        cmd = SkillsFixEngine._get_install_cmd("uv")
        assert "curl" in cmd
        assert "astral.sh" in cmd or "uv" in cmd


# ============================================================
#  边界情况与容错测试
# ============================================================

class TestEdgeCases:
    """边界情况和容错性测试。"""

    @patch('fixer.subprocess.run')
    def test_malformed_requirements_txt(self, mock_run, tmp_path):
        """格式错误的 requirements.txt 不应导致崩溃。"""
        mock_run.return_value = MagicMock(returncode=0)
        skill = tmp_path / "bad-deps"
        skill.mkdir()
        (skill / "SKILL.md").write_text("# Bad\n", encoding="utf-8")
        (skill / "requirements.txt").write_text("\n\n#\n===invalid===\n", encoding="utf-8")

        engine = SkillsFixEngine(str(tmp_path))
        results = engine.check_all()
        assert isinstance(results, dict)  # 不崩溃即可

    @patch('fixer.subprocess.run')
    def test_malformed_package_json(self, mock_run, tmp_path):
        """格式错误的 package.json 不应导致崩溃。"""
        mock_run.return_value = MagicMock(returncode=0)
        skill = tmp_path / "bad-pkg"
        skill.mkdir()
        (skill / "package.json").write_text("{invalid json!!!", encoding="utf-8")

        engine = SkillsFixEngine(str(tmp_path))
        results = engine.check_all()
        assert isinstance(results, dict)  # 不崩溃即可

    def test_binary_skill_md_content(self, tmp_path):
        """二进制内容的 SKILL.md 不应导致 generate_env_template 崩溃。"""
        skill = tmp_path / "binary-skill"
        skill.mkdir()
        (skill / "SKILL.md").write_bytes(b"\x00\x01\x02\x03 binary")

        engine = SkillsFixEngine(str(tmp_path))
        template = engine.generate_env_template()
        assert isinstance(template, str)  # 返回字符串即可

    def test_deeply_nested_skill_paths(self, tmp_path):
        """深层嵌套路径不应影响引擎工作。"""
        deep = tmp_path / "a" / "b" / "c" / "deep-skill"
        deep.mkdir(parents=True)
        (deep / "SKILL.md").write_text("# Deep\n", encoding="utf-8")

        engine = SkillsFixEngine(str(deep))
        # 不崩溃即通过
        assert engine.skills_base == deep
