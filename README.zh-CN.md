# 🛡️ Skills Health Guardian

<p align="center">
  <img src="assets/logo.png" alt="SHG Logo" width="120" height="120">
</p>

<p align="center">
  <strong>Skills 环境·健康管家</strong> — 扫描 → 诊断 → 报告 → 修复，全方位的 Skills 环境运维工具
</p>

<p align="center">
  <a href="#version"><img src="https://img.shields.io/badge/version-v1.0.0-blue.svg" alt="Version"></a>
  <a href="#license"><img src="https://img.shields.io/badge/license-MIT-green.svg" alt="License"></a>
  <a href="#"><img src="https://img.shields.io/badge/python-3.12%2B-yellow.svg" alt="Python Version"></a>
  <a href="#docker-support"><img src="https://img.shields.io/badge/Docker-4_modes-blueviolet.svg" alt="Docker Modes"></a>
  <a href="#cicd"><img src="https://img.shields.io/badge/CI%2FCD-GitHub_Actions-success" alt="CI/CD"></a>
  <a href="#health-score"><img src="https://img.shields.io/badge/Health_Score-76.8%2F100-orange" alt="Health Score"></a>
</p>

---

## ✨ 简介

Skills Health Guardian (简称 **SHG**) 是一个专为 WorkBuddy Agent Skills 生态设计的**环境健康巡检工具**。

当你安装了数十个 Skills，每个都有不同的依赖、运行时要求和 API Key 配置——如何确保它们都能正常工作？**SHG 就是答案。**

它像一位经验丰富的"体检医生"，自动扫描你所有的 Skills，检测依赖缺失、版本冲突、配置遗漏等问题，生成直观的健康报告，并提供一键修复能力。

> **零外部依赖 · 纯 Python 标准库实现 · 即装即用**

---

## 🤔 为什么需要它？

| 痛点 | 场景 | 后果 |
|------|------|------|
| 🔧 **运行时冲突** | Skill A 需要 Node.js 18+，Skill B 需要 Python 3.10 | 部分功能静默失败 |
| 📦 **版本冲突** | 两个 Skill 要求不同版本的同一包（如 `requests`） | `ImportError` 或行为异常 |
| 🔑 **API Key 缺失** | 安装了 OpenAI Skill 但未配置 `OPENAI_API_KEY` | 运行时报错，体验断裂 |
| 🌐 **网络依赖未知** | 某些 Skill 需要访问特定域名但文档未说明 | 企业内网环境下无法使用 |
| 📊 **整体状况不明** | 安装了 70+ 个 Skills，不知道哪些能用 | 浪费时间逐个调试 |
| ⏰ **缺乏持续监控** | 新安装 Skill 后引入冲突，无人知晓 | 问题积累到爆发才被发现 |

**SHG 让这一切变得透明可控。**

---

## 🎯 功能特性

| 特性 | 说明 |
|------|------|
| 🫁 **全面扫描** | 自动发现所有 SKILL.md / scripts / package.json，提取依赖和运行时需求 |
| 📊 **健康评分** | 0–100 分制，四级评分体系（健康 / 良好 / 警告 / 异常），一眼看懂全局状态 |
| ⚠️ **智能冲突检测** | 自动识别 Python 包版本冲突、Node.js 版本要求冲突、运行时资源竞争 |
| 🔧 **一键修复引擎** | 自动安装缺失依赖和运行时，生成 `.env` 模板文件，建议隔离方案 |
| 📋 **多格式报告** | 支持 Markdown / JSON / HTML 三种输出格式 + 30 天趋势追踪对比 |
| 💻 **CLI 增强模式** | 12 项命令行参数：格式切换、Watch 模式、彩色输出、单 Skill 精准扫描等 |
| 🐳 **Docker 一键部署** | 4 种运行模式：CLI / MCP Server / Web Dashboard / Cron 定时巡检 |
| 🔄 **CI/CD 集成** | 开箱即用的 GitHub Actions 流水线 + Makefile 快捷命令 |

---

## 🚀 快速开始

### 前提条件

- Python **3.12 或更高版本**
- macOS 或 Linux（Windows 可通过 WSL 使用）

### 安装

```bash
# 克隆仓库
git clone https://github.com/workbuddy-ai/skills-health-guardian.git
cd skills-health-guardian

# 赋予执行权限
chmod +x scripts/health-check.sh
```

> **无需 pip install！** SHG 使用纯 Python 标准库，零外部依赖。

### 三步上手

```bash
# 第一步：全量扫描
./scripts/health-check.sh --scan

# 第二步：查看健康报告
./scripts/health-check.sh --report markdown

# 第三步：（可选）一键修复
./scripts/health-check.sh --fix --auto
```

完成！你的终端会输出类似这样的结果：

```
╔══════════════════════════════════════════════╗
║   🛡️  Skills Health Guardian v1.0.0          ║
║   全局健康指数: 76.8/100 ★★★☆               ║
╠══════════════════════════════════════════════╣
║   ✅ 健康: 42    ⚠️  警告: 19    ❌ 异常: 10 ║
║   📦 依赖项总数: 289                         ║
╚══════════════════════════════════════════════╝
```

---

## 💻 使用示例

### 基础用法

| 命令 | 说明 |
|------|------|
| `./scripts/health-check.sh --scan` | 执行全量扫描 |
| `./scripts/health-check.sh --report json` | 输出 JSON 格式报告 |
| `./scripts/health-check.sh --report html` | 生成 HTML 可视化仪表盘 |
| `./scripts/health-check.sh --skill "frontend-developer"` | 仅扫描指定 Skill |

### 高级用法

| 命令 | 说明 |
|------|------|
| `./scripts/health-check.sh --watch` | **Watch 模式** — 每 60 秒自动重新扫描 |
| `./scripts/health-check.sh --fix --auto` | **自动修复** — 一键修复所有可处理的问题 |
| `./scripts/health-check.sh --fix --dry-run` | **预演模式** — 显示将要执行的修复操作但不实际执行 |
| `./scripts/health-check.sh --no-color` | 关闭彩色输出（适合日志收集） |
| `./scripts/health-check.sh --verbose` | 详细输出模式（显示每个 Skill 的完整诊断信息） |
| `./scripts/health-check.sh --output ./report.md` | 自定义报告输出路径 |
| `./scripts/health-check.sh --trend` | 启用 30 天趋势追踪对比 |

### 组合示例

```bash
# 监控模式下输出 JSON 到指定文件，同时启用趋势追踪
./scripts/health-check.sh --watch --report json --output ./reports/live.json --trend

# 对单个 Skill 进行详细扫描并自动修复
./scripts/health-check.sh --skill "ai-engineer" --verbose --fix --auto

# 生成 HTML 仪表盘报告并打开浏览器
./scripts/health-check.sh --report html --output ./reports/dashboard.html
```

---

## 📊 健康评分标准

SHG 采用 **0–100 分制**的健康评分体系，综合评估每个 Skill 的环境状态：

| 等级 | 分数范围 | 徽章 | 含义 |
|------|----------|------|------|
| 🟢 **健康 (Healthy)** | 90 – 100 | ✅ | 所有依赖就绪，无冲突，可正常使用 |
| 🟡 **良好 (Good)** | 70 – 89 | ⚠️ | 存在轻微问题（如可选依赖缺失），不影响核心功能 |
| 🟠 **警告 (Warning)** | 50 – 69 | ⚡ | 有明显问题需要关注（版本冲突或关键配置缺失） |
| 🔴 **异常 (Critical)** | 0 – 49 | ❌ | 存在严重问题，Skill 很可能无法正常运行 |

### 扣分规则

| 扣分项 | 分值 | 说明 |
|--------|------|------|
| 缺失必需依赖 | -15 / 每个 | 必须的包或运行时未安装 |
| 缺失可选依赖 | -5 / 每个 | 非必需但推荐安装的项 |
| API Key 未配置 | -10 / 每个 | 环境变量中缺少所需密钥 |
| 版本不兼容 | -20 / 每个 | 已安装版本低于最低要求 |
| 版本冲突 | -25 / 每个 | 多个 Skill 要求不同版本的同一依赖 |
| 脚本不可执行 | -10 / 每个 | scripts/ 中的脚本缺少执行权限 |

> **注意**：每个 Skill 最低得分为 0 分，不会出现负分。

---

## 🏗️ 架构设计

SHG 采用**四层管道架构**，每层职责清晰，易于扩展：

```
┌─────────────────────────────────────────────────────────────┐
│                     CLI / API 入口层                        │
│            health-check.sh / Web UI / MCP Server             │
└─────────────────────┬───────────────────────────────────────┘
                      │
                      ▼
┌─────────────────────────────────────────────────────────────┐
│                   🔍 Scanner 扫描层                         │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐         │
│  │ SKILL.md    │  │ scripts/    │  │ package.json │         │
│  │ 解析器       │  │ 分析器      │  │ 提取器       │         │
│  └─────────────┘  └─────────────┘  └─────────────┘         │
└─────────────────────┬───────────────────────────────────────┘
                      │
                      ▼
┌─────────────────────────────────────────────────────────────┐
│                   📊 Scorer 评分层                          │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐   │
│  │ 依赖检查  │→│ 冲突检测  │→│ 配置验证  │→│ 综合打分  │   │
│  └──────────┘  └──────────┘  └──────────┘  └──────────┘   │
└─────────────────────┬───────────────────────────────────────┘
                      │
                      ▼
┌─────────────────────────────────────────────────────────────┐
│              🔧 Fixer 修复层 & 📋 Reporter 报告层           │
│  ┌────────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐  │
│  │ 依赖安装   │  │ .env 生成 │  │ Markdown │  │ JSON     │  │
│  │ 运行时安装  │  │ 隔离建议  │  │ HTML     │  │ Trend    │  │
│  └────────────┘  └──────────┘  └──────────┘  └──────────┘  │
└─────────────────────────────────────────────────────────────┘
```

**数据流向**：`原始输入 → 结构化提取 → 规则引擎评估 → 行动建议输出`

---

## 📁 文件结构

```
skills-health-guardian/
├── README.zh-CN.md                 # ← 你在这里（中文版）
├── README.md                       # 英文版 README
├── SKILL.md                        # Skill 定义文件
├── LICENSE                         # MIT 许可证
│
├── assets/                         # 静态资源
│   ├── logo.png                    # SHG Logo (S 形盾牌)
│   └── favicon.ico                 # 图标
│
├── scripts/                        # 核心脚本
│   ├── scanner.py                  # 🔍 依赖与运行时扫描器
│   ├── reporter.py                 # 📋 多格式报告生成器
│   ├── fixer.py                    # 🔧 智能修复引擎
│   ├── health-check.sh             # 🚀 CLI 一键入口
│   └── scorer.py                   # 📊 健康评分引擎
│
├── templates/                      # 报告模板
│   ├── report.md.j2                # Markdown 模板
│   ├── report.html.j2              # HTML 仪表盘模板
│   └── env.template.j2             # .env 生成模板
│
├── docker/
│   ├── Dockerfile                  # Docker 镜像构建文件
│   ├── docker-compose.yml          # Docker Compose 编排（4 profiles）
│   └── entrypoint.sh               # 容器入口脚本
│
├── .github/
│   └── workflows/
│       ├── ci.yml                  # CI 流水线（lint + test + scan）
│       └── release.yml             # CD 流水线（自动发布）
│
├── tests/                          # 测试套件
│   ├── test_scanner.py             # 扫描器测试
│   ├── test_scorer.py              # 评分引擎测试
│   ├── test_fixer.py               # 修复引擎测试
│   └── test_reporter.py            # 报告生成测试
│
└── docs/                           # 详细文档
    ├── architecture.md             # 架构设计文档
    ├── cli-reference.md            # CLI 完整参考手册
    └── api-documentation.md        # MCP/Web API 文档
```

---

## 🖥️ 截图 / Demo

### 终端输出效果

运行基础扫描后，你会看到类似以下的彩色终端输出：

```
🛡️  Skills Health Guardian v1.0.0
═════════════════════════════════════

📅 扫描时间: 2026-04-04 10:30:00
📂 Skills 目录: ~/.workbuddy/skills/

┌────────────────────────────────────────────┐
│  全局健康指数:  76.8 / 100  ★★★☆           │
├────────────────────────────────────────────┤
│  ✅ 健康:    42  Skills                    │
│  ⚠️  良好/警告: 19  Skills                 │
│  ❌ 异常:    10  Skills                    │
│                                            │
│  📦 总依赖项: 289                          │
│  ⚠️  发现冲突: 3                            │
└────────────────────────────────────────────┘

Top 5 异常 Skills:
  1. ❌ openai-gpt (32/100) — 缺少 OPENAI_API_KEY
  2. ❌ anthropic-claude (35/100) — 缺少 ANTHROPIC_API_KEY
  3. ❌ database-optimizer (40/100) — PostgreSQL 未安装
  4. ⚠️ browser-agent (58/100) — playwright 依赖缺失
  5. ⚠️ image-gen (62/100) — API endpoint 配置有误
```

### HTML 仪表盘效果

使用 `--report html` 生成的暗色主题仪表盘，包含：
- 📈 健康分数环形图
- 🏷️ Skills 标签云（按类别分组）
- 📉 30 天趋势折线图
- 🔍 交互式筛选面板

> *截图占位：实际效果请运行 `./scripts/health-check.sh --report html` 查看*

---

## 🐳 Docker 支持

SHG 提供 4 种 Docker 运行模式，满足不同场景需求：

```bash
# 构建镜像
docker build -t shg:latest -f docker/Dockerfile .
```

| 模式 | 命令 | 说明 |
|------|------|------|
| **CLI 模式** | `docker run --rm -v ~/.workbuddy:/data shg:latest --scan` | 一次性扫描，输出到终端 |
| **MCP 模式** | `docker-compose --profile mcp up -d` | 作为 MCP Server 暴露给 AI Agent |
| **Web 模式** | `docker-compose --profile web up -d` | 启动 Web Dashboard（默认端口 8080） |
| **Cron 模式** | `docker-compose --profile cron up -d` | 定时巡检，报告推送到指定目录 |

### Docker Compose 快速启动

```bash
# Web Dashboard 模式（推荐首次使用）
docker compose --profile web up -d
# 访问 http://localhost:8080

# MCP Server 模式（集成到 WorkBuddy）
docker compose --profile mcp up -d
# 默认通过 stdio 暴露 MCP 协议接口

# Cron 定时巡检模式（每日自动扫描）
docker compose --profile cron up -d
# 报告输出至 ./reports/ 目录
```

---

## 🔄 CI/CD

SHG 内置 GitHub Actions 工作流，支持自动化测试和发布：

### CI 流水线 (`ci.yml`)

每次 Push 和 PR 自动触发：
1. **Lint 检查** — Python 代码风格 + Shell 脚本检查
2. **单元测试** — 4 大模块全覆盖测试
3. **集成扫描** — 使用测试 Skill 集运行完整扫描流程

### CD 流水线 (`release.yml`)

创建新 Tag 时自动触发：
1. 构建多架构 Docker 镜像（linux/amd64 + linux/arm64）
2. 推送到 GitHub Container Registry (ghcr.io)
3. 生成 GitHub Release 附带变更日志

### 本地 Makefile 快捷命令

```bash
make lint          # 运行代码检查
make test          # 运行全部测试
make scan          # 执行本地扫描
make report        # 生成报告
make docker-build  # 构建 Docker 镜像
make release       # 创建新版本发布
```

---

## 🤝 贡献指南

我们欢迎任何形式的贡献！无论是 Bug 修复、功能增强还是文档改进。

### 如何参与

1. **Fork** 本仓库
2. 创建特性分支：`git checkout -b feature/amazing-feature`
3. 提交更改：`git commit -m '✨ add amazing feature'`
4. 推送到分支：`git push origin feature/amazing-feature`
5. 提交 **Pull Request**

### 开发规范

- 遵循 **纯标准库原则** —— 不引入外部 Python 依赖
- 新增功能需附带对应的 **单元测试**
- Commit message 参考 [Conventional Commits](https://www.conventionalcommits.org/) 规范
- 代码风格遵循 **PEP 8**

---

## 📄 许可证

本项目采用 [MIT License](LICENSE) 开源协议。

```
Copyright (c) 2026 tomansen (https://github.com/tomansen)

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software...
```

---

## 🙏 致谢

- **WorkBuddy Team** — 打造了精彩的 Agent Skills 生态 🚀
- **开源社区** — 无数优秀工具给予灵感 ✨
- **[Your Name]** — 感谢每一个 Star 和贡献者 ⭐

<div align="center">

如果 SHG 对你有帮助，不妨给个 ⭐ **Star** 支持一下！

**让每一个 Skill 都能健康运行** 🛡️💙

<a href="#top">回到顶部 ↑</a>

</div>
