---
name: skills-health-guardian
description: "Skills 环境健康管家 — 自动巡检所有 Agent Skills 的运行环境依赖、版本冲突、API Key 配置状态，生成健康报告，提供自动修复建议，并支持定期巡检和趋势追踪。触发词：环境检查、skill检查、依赖冲突、环境健康、环境巡检、skills scan、health check、环境维护、技能管理。"
version: "1.0.0"
metadata:
  author: WorkBuddy AI
  license: MIT
---

# 🏥 Skills 环境 Health Guardian (健康管家)

> **一句话**: 扫描 → 诊断 → 报告 → 修复 — 全方位的 Skills 环境运维工具。

## 为什么需要它？

随着 skills 数量增长（当前 **68+** 个），以下问题越来越常见：

| 问题 | 示例 | 影响 |
|------|------|------|
| **运行时冲突** | Skill A 需要 `uv`，Skill B 需要 `bun`，都没装 | 脚本直接报错 |
| **Python 版本冲突** | `pillow>=10` vs 项目全局 `pillow==9.1` | 隐式降级或崩溃 |
| **API Key 缺失** | `GEMINI_API_KEY` 未设置但 skill 需要 | 运行时才暴露问题 |
| **依赖漂移** | 上月装好的包，系统更新后路径变了 | 无声失败 |
| **Chrome/浏览器** | Playwright 类 skill 依赖特定 Chrome 版本 | CDP 连接超时 |

## 架构总览

```
┌──────────────────────────────────────────────────────┐
│              Skills Health Guardian                  │
├─────────────┬────────────────────────────────────────┤
│  🔍 scanner │  扫描所有 SKILL.md / scripts / pkg.json  │
│             │  提取依赖、运行时需求、环境变量           │
├─────────────┼────────────────────────────────────────┤
│  ⚡ fixer   │  一键安装缺失运行时                      │
│             │  自动修复缺失依赖                        │
│             │  生成 .env.template 模板                 │
│             │  建议虚拟环境隔离方案                     │
├─────────────┼────────────────────────────────────────┤
│  📊 reporter│  Markdown / JSON / HTML 报告            │
│             │  健康评分 + 趋势追踪 (30天)              │
│             │  智能修复建议                            │
└─────────────┴────────────────────────────────────────┘
```

## 快速使用

### 1️⃣ 完整健康报告（最常用）

```bash
# 终端输出友好报告
python3 ~/.workbuddy/skills/skills-health-guardian/scripts/scanner.py

# 导出 JSON
python3 ~/.workbuddy/skills/skills-health-guardian/scripts/scanner.py --json -o report.json

# 仅扫描指定 skill
python3 ~/.workbuddy/skills/skills-health-guardian/scripts/scanner.py --skill url-reader

# 使用一键脚本
~/.workbuddy/skills/skills-health-guardian/scripts/health-check.sh
```

### 2️⃣ 检查可修复项

```bash
python3 ~/.workbuddy/skills/skills-health-guardian/scripts/fixer.py check
```

### 3️⃣ 自动修复

```bash
# 预览模式（推荐先跑这个）
python3 ~/.workbuddy/skills/skills-health-guardian/scripts/fixer.py fix runtime uv --dry-run

# 安装缺失运行时
python3 ~/.workbuddy/skills/skills-health-guardian/scripts/fixer.py fix runtime uv -y

# 安装指定 skill 的依赖
python3 ~/.workbuddy/skills/skills-health-guardian/scripts/fixer.py fix deps url-reader -y

# 生成环境变量模板
python3 ~/.workbuddy/skills/skills-health-guardian/scripts/fixer.py env-template

# 查看隔离方案建议
python3 ~/.workbuddy/skills/skills-health-guardian/scripts/fixer.py fix isolate
```

### 4️⃣ 生成完整报告（Markdown/HTML）

```bash
# Markdown 格式（默认，含趋势）
python3 ~/.workbuddy/skills/skills-health-guardian/scripts/reporter.py -f markdown

# HTML 可视化报告
python3 ~/.workbuddy/skills/skills-health-guardian/scripts/reporter.py -f html

# JSON 机器可读格式
python3 ~/.workbuddy/skills/skills-health-guardian/scripts/reporter.py -f json
```

## 健康评分标准

| 分数范围 | 状态 | 含义 |
|----------|------|------|
| **80 - 100** | 🟢 健康 | 所有依赖就绪，无阻塞问题 |
| **50 - 79** | 🟡 警告 | 有缺失项但不影响核心功能 |
| **0 - 49** | 🔴 异常 | 关键运行时缺失或有严重冲突 |

**扣分规则：**
- 无 SKILL.md → -15
- 有脚本但无依赖声明 → -5
- 缺少运行时工具 → 每个 -15
- 未设置 API Key 环境变量 → 每个 -5（最多 -20）
- 有 Python 脚本但无 python3 → -20

## 输出报告示例

### 终端快速预览

```
═══════════════════════════════════════
  🏥 Skills 环境健康报告
═══════════════════════════════════════
  📊 扫描时间: 2026-04-04 08:57:00
  📦 Skill 总数: 68

  🌡️ 全局健康指数: 76.2/100  [████████░░░░░░░░░░░░░░░]

  ✅ 健康 (≥80): 42
  ⚠️ 警告 (50-79): 18
  🔴 异常 (<50): 8

  🔧 运行时需求: bun, npx, node, uv, playwright
  🔑 环境变量需求: GEMINI_API_KEY, FIRECRAWL_API_KEY, ...

  ⚡ 全局冲突与警告:
     ⚠️ 依赖版本冲突: pillow
        - nano-banana-pro: 要求 >=10.0 (pip)
        - 其他项目: 要求 ==9.1 (pip)

  📋 各 Skill 详情:
    ...
```

### HTML 可视化报告

Reporter 支持输出带样式的 HTML 报告，包含：
- 大号健康分数仪表盘
- 各 Skill 详情表格（按健康分排序）
- 运行时状态矩阵
- 智能修复建议

## 文件结构

```
skills-health-guardian/
├── SKILL.md                  # ← 你正在读的这个文件
└── scripts/
    ├── scanner.py             # 核心扫描器（依赖提取 + 冲突检测 + 评分）
    ├── reporter.py            # 报告生成器（MD/JSON/HTML + 趋势追踪）
    ├── fixer.py               # 自动修复引擎（安装/隔离/模板生成）
    └── health-check.sh        # 一键巡检 shell 入口
```

## 工作流集成方式

### 作为 AI Agent 触发

当用户说以下任意关键词时，加载此 skill：

> "检查一下 skills 环境" / "环境健康吗" / "依赖有没有冲突" / 
> "skill 能用吗" / "run health check" / "环境巡检"

**标准工作流：**

1. **扫描** — 运行 `scanner.py` 获取全量快照
2. **分析** — 关注 🔴 异常项和 ⚠️ 版本冲突
3. **汇报** — 用 `reporter.py` 生成格式化报告
4. **修复**（可选）— 用户确认后用 `fixer.py` 执行修复

### 定期自动化巡检

支持两种方式实现每日/每周自动巡检：

#### 方式一：WorkBuddy Automation（推荐）

在 WorkBuddy 中配置自动化任务：

- **名称**: Skills 环境健康每日巡检
- **调度**: `FREQ=DAILY;BYHOUR=9;BYMINUTE=0`（每天早上 9 点）
- **工作目录**: `/Users/tomansen/.workbuddy/skills/skills-health-guardian`
- **任务描述**: 运行 `python3 scripts/scanner.py && python3 scripts/reporter.py -f markdown`，将报告保存到 `reports/` 目录
- **状态**: ACTIVE

> 💡 如果 Automation API 暂时不可用，使用方式二作为备选。

#### 方式二：系统 Crontab（通用备选）

编辑 crontab 添加定时任务：

```bash
crontab -e
```

添加以下内容（根据需要选择）：

```bash
# ====== Skills 环境健康巡检 ======

# 每天早 9 点生成 Markdown 报告
0 9 * * * bash ~/.workbuddy/skills/skills-health-guardian/scripts/health-check.sh report >> /tmp/skills-health-cron.log 2>&1

# 每周一 10 点生成 HTML 可视化报告
0 10 * * 1 bash ~/.workbuddy/skills/skills-health-guardian/scripts/health-check.sh report -f html >> /tmp/skills-health-cron.log 2>&1

# 每 6 小时仅做快速检查（不生成报告，日志记录即可）
0 */6 * * * python3 ~/.workbuddy/skills/skills-health-guardian/scripts/scanner.py >> /tmp/skills-health-cron.log 2>&1
```

**验证 cron 是否生效：**

```bash
# 查看已注册的定时任务
crontab -l

# 手动触发一次测试
bash ~/.workbuddy/skills/skills-health-guardian/scripts/health-check.sh report

# 查看运行日志
tail -20 /tmp/skills-health-cron.log
```

> ⚠️ **macOS 注意事项**：macOS 可能阻止后台 cron 执行某些 GUI 相关检查。建议在 `scanner.py` 中使用 `--no-gui-check` 参数跳过浏览器检测（如果支持），或确保 cron 环境中有正确的 `PATH`。

## 数据持久化

```
~/.workbuddy/skills/skills-health-guardian/
└── reports/
    ├── health-report-2026-04-04_09-00-00.md   # 最新报告
    ├── health-report-2026-04-03_09-00-00.md   # 历史报告
    ├── history/
    │   ├── 2026-04-04.json                    # 当日快照（可能多次）
    │   ├── 2026-04-03.json                    # ...
    │   └── ...                                # 最多保留 30 天
    └── .env.template                          # 环境变量模板
```

## 高级用法

### 自定义扫描目录

默认扫描 `~/.workbuddy/skills`，可通过 `--path` 指定其他位置：

```bash
python3 scanner.py --path /path/to/other/skills
```

### 与 CI/CD 集成

在 pipeline 中加入环境健康门禁：

```yaml
# GitHub Actions 示例
- name: Skills Health Check
  run: |
    python3 skills-health-guardian/scripts/scanner.py --json > health.json
    python3 -c "
    import json
    d = json.load(open('health.json'))
    score = d['summary']['avg_health_score']
    assert score >= 70, f'Health score {score} too low!'
    print(f'Health check passed: {score}/100')
"
```

### 多平台支持

- ✅ macOS（原生支持，含 Chrome 检测）
- ✅ Linux（bash + python3 兼容）
- ⚠️ Windows（需 WSL 或 Git Bash）

## 与现有工具的关系

| 功能 | 本 Skill | skills-security-check | 手动检查 |
|------|---------|-----------------------|---------|
| 依赖检测 | ✅ 全面 | ❌ 不涉及 | 逐个看 SKILL.md |
| 运行时冲突 | ✅ 自动发现 | ❌ 不涉及 | 靠踩坑 |
| API Key 状态 | ✅ 汇总展示 | ❌ 不涉及 | 记不住 |
| 安全审计 | ⚠️ 基础版 | ✅ 深度安全 | N/A |
| 自动修复 | ✅ 一键修复 | ❌ 不涉及 | 手动操作 |
| 趋势追踪 | ✅ 30天历史 | ❌ 不涉及 | 无 |

**互补关系**：`skills-health-guardian` 负责**环境和依赖**层面的健康管理，`skills-security-check` 负责**代码安全性**审查。两者配合使用效果最佳。

## 更新日志

- **v1.0.0** (2026-04-04): 初始发布
  - 核心扫描器：SKILL.md / package.json / *.py 依赖提取
  - 冲突检测：Python 包版本 + 运行时高频使用
  - 健康评分：0-100 分制
  - 报告生成：Markdown / JSON / HTML 三种格式
  - 自动修复引擎：运行时安装 + 依赖安装 + env template + 隔离建议
  - 趋势追踪：最近 30 天历史快照
  - 一键 shell 入口脚本
  - 双模式自动化巡检：WorkBuddy Automation + Crontab（备选）
