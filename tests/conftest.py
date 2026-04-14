"""
共享测试 fixtures — 为 scanner/reporter/fixer 测试提供临时数据
"""

import pytest
import json


# ============================================================
#  Fixtures: 临时 Skill 目录结构
# ============================================================

@pytest.fixture
def sample_skill_dir(tmp_path):
    """
    创建一个完整 skill 目录结构（含 SKILL.md, Python 脚本等）
    用于测试扫描器能正确发现和解析文件。
    """
    # SKILL.md
    (tmp_path / "SKILL.md").write_text("""---
name: test-skill
description: A test skill for QA
---

# Test Skill

## 安装

```bash
pip install requests>=2.28 beautifulsoup4
```

## 运行

使用 `uv run` 启动。

需要环境变量 `OPENAI_API_KEY`。
""", encoding="utf-8")

    # scripts 目录
    scripts_dir = tmp_path / "scripts"
    scripts_dir.mkdir()

    (scripts_dir / "main.py").write_text(
        '#!/usr/bin/env python3\n'
        '"""Main script for test-skill."""\n'
        "import requests\n"
        "from bs4 import BeautifulSoup\n"
        "import os\n\n"
        'api_key = os.environ.get("OPENAI_API_KEY", "")\n'
        "uv run app.py  # noqa: F821\n",
        encoding="utf-8")

    (scripts_dir / "helper.sh").write_text("""\
#!/bin/bash
pip3 install click
npm install -g typescript
npx tsc --version
""", encoding="utf-8")

    return tmp_path


@pytest.fixture
def empty_skill_dir(tmp_path):
    """创建空目录，用于测试边界情况。"""
    return tmp_path


@pytest.fixture
def invalid_skill_dir(tmp_path):
    """创建一个有损坏 SKILL.md 的目录，测试容错能力。"""
    (tmp_path / "SKILL.md").write_text("{{{INVALID CONTENT\n\n<<<>>> broken", encoding="utf-8")
    bad_scripts = tmp_path / "scripts"
    bad_scripts.mkdir()
    (bad_scripts / "bad.py").write_text("\x00\x01\x02 binary garbage", encoding="utf-8")
    return tmp_path


@pytest.fixture
def multi_skill_base(tmp_path):
    """创建含多个 skill 子目录的基础路径，用于全量扫描和冲突检测测试。"""

    # Skill A: 健康 skill
    skill_a = tmp_path / "skill-a"
    skill_a.mkdir()
    (skill_a / "SKILL.md").write_text("---\nname: skill-a\n---\n# A\npip install numpy", encoding="utf-8")
    sa_scripts = skill_a / "scripts"
    sa_scripts.mkdir()
    (sa_scripts / "calc.py").write_text("import numpy\narr = numpy.array([1,2,3])\n", encoding="utf-8")

    # Skill B: 有运行时需求
    skill_b = tmp_path / "skill-b"
    skill_b.mkdir()
    (skill_b / "SKILL.md").write_text("---\nname: skill-b\n---\n# B\nUses bun and npx.\n", encoding="utf-8")
    sb_scripts = skill_b / "scripts"
    sb_scripts.mkdir()
    (sb_scripts / "index.ts").write_text('import express from "express";\nconst app = express();\n', encoding="utf-8")

    # Skill C: 无 SKILL.md
    skill_c = tmp_path / "skill-c"
    skill_c.mkdir()
    sc_scripts = skill_c / "scripts"
    sc_scripts.mkdir()
    (sc_scripts / "run.py").write_text("# just a script\nprint(42)\n", encoding="utf-8")

    # Skill D: 含 package.json
    skill_d = tmp_path / "skill-d"
    skill_d.mkdir()
    (skill_d / "SKILL.md").write_text("---\nname: skill-d\n---\n# D\n", encoding="utf-8")
    pkg = {
        "dependencies": {"react": "^18.0.0", "lodash": "^4.0.0"},
        "devDependencies": {"typescript": "^5.0.0"}
    }
    (skill_d / "package.json").write_text(json.dumps(pkg), encoding="utf-8")

    return tmp_path


@pytest.fixture
def mock_scan_result():
    """
    模拟的扫描结果数据字典，格式与 scanner.to_json() 输出一致。
    用于 reporter 测试的输入。
    """
    return {
        "summary": {
            "total_skills": 3,
            "avg_health_score": 76.7,
            "healthy_count": 1,
            "warning_count": 1,
            "critical_count": 1,
            "skills_with_scripts": 3,
            "skills_with_dependencies": 2,
            "total_dependencies": 5,
            "unique_runtimes": ["python3", "uv"],
            "unique_env_vars": ["OPENAI_API_KEY", "NOTION_TOKEN"],
            "global_issues": [
                {
                    "type": "version_conflict",
                    "dependency": "requests",
                    "usages": [
                        {"skill": "skill-a", "version": ">=2.28", "type": "pip"},
                        {"skill": "skill-b", "version": "==2.25.0", "type": "pip"},
                    ],
                    "severity": "warning"
                },
                {
                    "type": "heavy_runtime_dependency",
                    "runtime": "node",
                    "used_by": ["skill-a", "skill-b", "skill-c", "skill-d"],
                    "count": 4,
                    "severity": "info"
                }
            ],
            "scan_time": "2026-04-04T10:20:00",
        },
        "skills": {
            "skill-a": {
                "name": "skill-a",
                "path": "/fake/skill-a",
                "has_scripts": True,
                "script_files": ["scripts/main.py"],
                "dependencies": [
                    {"name": "requests", "version_spec": ">=2.28", "dep_type": "pip", "source_file": "scripts/main.py"},
                ],
                "runtime_requirements": [],
                "env_vars": ["OPENAI_API_KEY"],
                "has_package_json": False,
                "has_requirements_txt": False,
                "has_pyproject_toml": False,
                "uses_uv": False,
                "uses_bun": False,
                "uses_npx": False,
                "skill_md_exists": True,
                "health_score": 85,
                "issues": [],
                "warnings": [],
                "last_scanned": "2026-04-04T10:19:00",
            },
            "skill-b": {
                "name": "skill-b",
                "path": "/fake/skill-b",
                "has_scripts": True,
                "script_files": ["scripts/index.js"],
                "dependencies": [
                    {"name": "requests", "version_spec": "==2.25.0", "dep_type": "pip", "source_file": "SKILL.md"},
                    {"name": "express", "version_spec": "", "dep_type": "npm", "source_file": "package.json"},
                ],
                "runtime_requirements": ["node", "npm"],
                "env_vars": ["NOTION_TOKEN"],
                "has_package_json": True,
                "has_requirements_txt": False,
                "has_pyproject_toml": False,
                "uses_uv": False,
                "uses_bun": True,
                "uses_npx": True,
                "skill_md_exists": True,
                "health_score": 65,
                "issues": ["缺少运行时: node"],
                "warnings": ["未设置环境变量: NOTION_TOKEN"],
                "last_scanned": "2026-04-04T10:19:30",
            },
            "skill-c": {
                "name": "skill-c",
                "path": "/fake/skill-c",
                "has_scripts": True,
                "script_files": ["scripts/run.py"],
                "dependencies": [
                    {"name": "click", "version_spec": ">=8.0", "dep_type": "pip", "source_file": "requirements.txt"},
                ],
                "runtime_requirements": [],
                "env_vars": [],
                "has_package_json": False,
                "has_requirements_txt": True,
                "has_pyproject_toml": False,
                "uses_uv": False,
                "uses_bun": False,
                "uses_npx": False,
                "skill_md_exists": False,
                "health_score": 40,
                "issues": ["缺少 SKILL.md 文件"],
                "warnings": [],
                "last_scanned": "2026-04-04T10:20:00",
            },
        }
    }


@pytest.fixture
def tmp_output_path(tmp_path):
    """临时输出路径，用于报告保存测试。"""
    out = tmp_path / "output"
    out.mkdir(exist_ok=True)
    return out
