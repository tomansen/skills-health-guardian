# 🐳 Skills Health Guardian — Docker 使用指南

> **Skills Health Guardian** 的容器化部署方案，支持 CLI 扫描、MCP Server 和 Web Dashboard 三种模式。

---

## 目录

- [快速开始](#快速开始)
- [构建镜像](#构建镜像)
- [运行模式](#运行模式)
  - [模式 1：CLI 扫描（一次性）](#模式-1cli-扫描一次性)
  - [模式 2：MCP Server（长驻服务）](#模式-2mcp-server长驻服务)
  - [模式 3：Web Dashboard（HTTP 服务）](#模式-3web-dashboardhttp-服务)
  - [模式 4：定时巡检（Cron）](#模式-4定时巡检cron)
- [环境变量](#环境变量)
- [Volume 映射说明](#volume-映射说明)
- [Docker 命令速查表](#docker-命令速查表)
- [常见问题 FAQ](#常见问题-faq)

---

## 快速开始

### 前置要求

| 工具 | 版本 | 说明 |
|------|------|------|
| Docker Engine | ≥ 20.10 | Linux/macOS/Windows |
| Docker Compose | ≥ 2.0 (V2) | `docker compose` (带空格) |

### 一键体验

```bash
# 克隆项目（如果还没有）
git clone https://github.com/tomansen/skills-health-guardian.git
cd skills-health-guardian

# 构建 + 运行一次完整扫描
docker build -t shg .
docker run --rm -v ~/.workbuddy/skills:/skills:ro shg
```

---

## 构建镜像

```bash
# 标准构建
docker build -t shg .

# 指定标签和版本
docker build -t shg:1.0.0 -t shg:latest .

# 无缓存重建（开发调试用）
docker build --no-cache -t shg .

# 多平台构建（需要 buildx）
docker buildx build --platform linux/amd64,linux/arm64 -t shg:latest .
```

### 镜像大小估算

| 层 | 大小 |
|----|------|
| python:3.13-slim 基础镜像 | ~150 MB |
| 系统依赖 (git, bash) | ~15 MB |
| Python 依赖 (rich) | ~5 MB |
| 项目源码 (scripts/) | ~50 KB |
| **总计（压缩后）** | **~75 MB** |

---

## 运行模式

### 模式 1：CLI 扫描（一次性）

最常用 — 扫描 skills 目录并输出健康报告。

#### 使用 docker run

```bash
# 基本扫描（表格输出）
docker run --rm \
  -v ~/.workbuddy/skills:/skills:ro \
  -v $(pwd)/reports:/app/reports \
  shg

# JSON 格式输出到 stdout
docker run --rm -v ~/.workbuddy/skills:/skills:ro \
  shg --path /skills --json

# 保存报告到文件
docker run --rm \
  -v ~/.workbuddy/skills:/skills:ro \
  -v $(pwd)/reports:/app/reports \
  shg --path /skills --output /app/reports/report.json

# 只扫描指定 skill
docker run --rm -v ~/.workbuddy/skills:/skills:ro \
  shg --skill url-reader
```

#### 使用 docker compose（推荐）

```bash
# 启动 CLI 扫描
docker compose --profile cli run shg-cli

# 自定义路径
SKILLS_PATH=/path/to/your/skills REPORT_DIR=./my-reports \
  docker compose --profile cli run shg-cli
```

---

### 模式 2：MCP Server（长驻服务）

以 stdio 模式运行 SHG MCP Server，供 AI Agent 调用。

> ⚠️ **注意**: MCP Server 功能正在开发中。当前为预留接口，启动后会显示占位消息。待 `server.py` 就绪后替换 `command` 即可。

```bash
# 启动 MCP Server（前台）
docker compose --profile mcp up shg-mcp

# 后台运行
docker compose --profile mcp up -d shg-mcp

# 查看日志
docker compose --profile mcp logs -f shg-mcp

# 停止
docker compose --profile mcp down
```

**MCP 配置参考**（待 server.py 发布后使用）：

```json
{
  "mcpServers": {
    "shg": {
      "command": "docker",
      "args": [
        "compose", "-f", "/path/to/docker-compose.yml",
        "--profile", "mcp", "run", "--rm", "shg-mcp"
      ]
    }
  }
}
```

---

### 模式 3：Web Dashboard（HTTP 服务）

自动执行扫描 → 生成 HTML 报告 → 启动 HTTP 服务器预览。

```bash
# 构建并启动 Web Dashboard
docker compose --profile web up -d shg-web --build

# 浏览器访问
open http://localhost:8080

# 自定义端口
WEB_PORT=9090 docker compose --profile web up -d shg-web
```

功能：
- 📊 自动扫描所有 skills 并生成 HTML 报告
- 🌙 暗色主题仪表盘 UI
- 📈 健康评分可视化
- 🔄 容器重启时自动重新扫描

---

### 模式 4：定时巡检（Cron）

在容器内按计划周期性扫描，结果持久化到 reports/ 目录。

```bash
# 每 6 小时扫描一次（默认）
docker compose --profile cron up -d shg-cron

# 自定义 cron 表达式
CRON_SCHEDULE="0 */12 * * *" docker compose --profile cron up -d shg-cron

# 每天 09:00 和 18:00 扫描
CRON_SCHEDULE="0 9,18 * * *" docker compose --profile cron up -d shg-cron
```

查看扫描历史：

```bash
ls -la reports/
cat reports/scan-20260404_090000.json
```

---

## 环境变量

| 变量名 | 默认值 | 说明 |
|--------|--------|------|
| `SKILLS_PATH` | `/skills` | 容器内 skills 目录挂载点 |
| `REPORT_DIR` | `/app/reports` | 报告输出目录 |
| `WEB_PORT` | `8080` | Web Dashboard 端口 |
| `CRON_SCHEDULE` | `*/6 * * * *` | Cron 模式调度表达式 |
| `PYTHONUNBUFFERED` | `1` | Python 输出不缓冲（固定开启） |
| `PYTHONDONTWRITEBYTECODE` | `1` | 不生成 .pyc 文件（固定开启） |

### 在 docker-compose 中覆盖环境变量

```bash
# 方式 1：命令行传入
SKILLS_PATH=/custom/path docker compose --profile cli run shg-cli

# 方式 2：.env 文件（项目根目录创建 .env）
echo "SKILLS_PATH=/home/me/my-skills" > .env
docker compose --profile cli run shg-cli

# 方式 3：compose 文件中直接修改 environment 段
```

---

## Volume 映射说明

### 核心映射关系

```
宿主机                          容器
─────────────────────────────────────────
~/.workbuddy/skills     ───→   /skills       (只读，扫描目标)
./reports               ───→   /app/reports   (读写，报告输出)
```

### 为什么 skills 目录是只读？

- ✅ 安全：防止误操作删除或修改 skill 文件
- ✅ 干净：每次扫描都是对宿主机文件的快照读取
- ✅ 高效：不需要复制整个 skills 目录进镜像

### macOS / Windows 路径注意事项

```bash
# macOS — 用 $HOME 展开
-v $HOME/.workbuddy/skills:/skills:ro

# Windows PowerShell
-v "$env:USERPROFILE\.workbuddy\skills:C:\skills:ro"

# Git Bash / WSL
-v ~/.workbuddy/skills:/skills:ro
```

---

## Docker 命令速查表

| 操作 | 命令 |
|------|------|
| 构建 | `docker build -t shg .` |
| 一次扫描 | `docker run --rm -v ~/.workbuddy/skills:/skills:ro shg` |
| CLI 模式 | `docker compose --profile cli run shg-cli` |
| MCP 模式 | `docker compose --profile mcp up shg-mcp` |
| Web 模式 | `docker compose --profile web up -d shg-web` |
| Cron 模式 | `docker compose --profile cron up -d shg-cron` |
| 查看日志 | `docker compose --profile web logs -f` |
| 停止所有 | `docker compose down` |
| 清理镜像 | `docker rmi shg:latest` |
| 进入容器调试 | `docker run --rm -it -v ~/.workbuddy/skills:/skills:ro shg bash` |

---

## 常见问题 FAQ

### Q1: `docker build` 报错找不到文件？

检查 `.dockerignore` 是否排除了必要文件：

```bash
# 调试：查看实际发送给 Docker daemon 的上下文
docker build --progress=plain -t shg . 2>&1 | head -20
```

确保以下文件**存在且未被排除**：
- ✅ `pyproject.toml`
- ✅ `scripts/scanner.py`, `scripts/reporter.py`, `scripts/fixer.py`
- ✅ `scripts/health-check.sh`
- ✅ `SKILL.md`

### Q2: 扫描结果全是 0 分？

Skills 目录没有正确挂载：

```bash
# 确认宿主机路径正确
ls ~/.workbuddy/skills | head -5

# 确认容器能看到文件
docker run --rm -v ~/.workbuddy/skills:/skills:ro shg ls /skills | head -5
```

### Q3: macOS Docker Desktop 性能慢？

macOS 文件系统挂载有已知性能问题。建议：

```bash
# 方案 A：使用本地缓存卷（推荐用于频繁操作）
docker volume create shg-cache
docker run --rm \
  -v shg-cache:/tmp/skills-copy \
  -v ~/.workbuddy/skills:/host-skills:ro \
  shg bash -c "cp -r /host-skills/* /tmp/skills-copy/ && python3 scripts/scanner.py --path /tmp/skills-copy"

# 方案 B：将 reports 也映射到内存
docker run --rm --tmpfs /app/reports \
  -v ~/.workbuddy/skills:/skills:ro shg
```

### Q4: 如何自定义安装额外依赖？

编辑 Dockerfile 或通过构建参数：

```bash
# 方式 1：构建参数
docker build --build-arg PIP_EXTRA_INDEX_URL=https://pypi.example.com/simple -t shg .

# 方式 2：扩展 Dockerfile（创建 Dockerfile.dev）
FROM sh:latest
RUN pip install --no-cache-dir pytest black mypy
```

### Q5: MCP Server 模式如何连接？

MCP Server 接口还在开发中。当前可以：

1. 使用 CLI 模式的 `--json` 输出获取机器可读数据
2. 关注项目 releases 获取 MCP Server 正式版

### Q6: ARM64 (Apple Silicon) 兼容吗？

✅ 完全兼容。`python:3.13-slim` 支持 `linux/arm64`。

```bash
# 确认架构
docker buildx inspect | grep Platforms
# 输出应包含: linux/amd64, linux/arm64
```

---

## 开发与贡献

如需修改 Docker 配置：

```bash
# 本地迭代：快速测试
docker build -t shg:dev . && \
docker run --rm -it -v ~/.workbuddy/skills:/skills:ro -v $(pwd):/app shg:dev bash

# 清理后重建
docker builder prune && docker build --no-cache -t shg .
```

---

*最后更新: 2026-04-04 by Sam-Docker @ SHG Team*
