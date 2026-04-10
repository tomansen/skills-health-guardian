# 故障排查指南 (Troubleshooting Guide)

> **Skills Health Guardian 常见问题快速解决方案**  
> **版本**: v1.0.1  
> **更新时间**: 2026-04-10
> **新增**: 跨平台兼容性支持（macOS/Linux/Windows）

---

## 🚨 快速诊断

| 问题症状 | 可能原因 | 解决方案（点击跳转）|
|---------|----------|----------------|
| ❌ Permission denied | 脚本没有执行权限 | [见问题 #3](#problem-3) |
| ❌ FileNotFoundError: scripts/ | 错误的运行目录 | [见问题 #2](#problem-2) |
| ❌ Python 版本不足 | Python < 3.12 | [见问题 #1](#problem-1) |
| ❌ ModuleNotFoundError | 缺少标准库模块 | [见问题 #7](#problem-7) |
| ❌ pip install 失败 | PyPI 未发布 | [见问题 #5](#problem-5) |
| ❌ Docker 构建失败 | 错误的构建上下文 | [见问题 #10](#problem-10) |

---

## 问题 #1: Python 版本不足

### 症状
```bash
❌ 错误: Python 版本不足
   Skills Health Guardian 需要 Python 3.12 或更高版本
   当前版本: Python 3.11.7
```

### 原因
Skills Health Guardian 使用了 Python 3.12+ 的新特性，旧版本不兼容。

### 解决方案

#### macOS
```bash
# 使用 Homebrew
brew install python@3.12
python3 --version  # 验证版本

# 设置为默认版本（可选）
echo 'eval "$(pyenv init -)"' >> ~/.zshrc
pyenv global 3.12.0
```

#### Linux (Ubuntu/Debian)
```bash
# 更新包列表
sudo apt update

# 安装 Python 3.12
sudo apt install python3.12 python3-pip

# 验证
python3.12 --version
```

#### Windows
1. 访问 [https://www.python.org/downloads/](https://www.python.org/downloads/)
2. 下载 Python 3.12 或更高版本的安装程序
3. 运行安装程序，确保勾选 "Add Python to PATH"
4. 重启命令行，验证:
   ```powershell
   python --version
   ```

### 验证
```bash
python3 --version
# 应该输出类似: Python 3.12.x
```

---

## 问题 #2: scripts 路径错误

### 症状
```bash
FileNotFoundError: [Errno 2] No such file or directory: 'scripts/scanner.py'
```

### 原因
在错误目录运行命令，或者目录结构不完整。

### 解决方案

#### 方案 A: 切换到正确目录（推荐）
```bash
# 从任意目录开始
git clone https://github.com/tomansen/skills-health-guardian.git

# 重要：必须进入项目根目录
cd skills-health-guardian

# 验证目录结构
ls scripts/
# 应该看到: scanner.py, reporter.py, fixer.py, health-check.sh, cli.py

# 运行命令
python3 scripts/scanner.py --help
```

#### 方案 B: 使用绝对路径
```bash
python3 /absolute/path/to/skills-health-guardian/scripts/scanner.py --help
```

### 验证
```bash
# 检查脚本是否存在
ls -la scripts/scanner.py

# 或者直接测试
python3 scripts/scanner.py --version
```

---

## 问题 #3: health-check.sh 权限问题

### 症状
```bash
bash: ./scripts/health-check.sh: Permission denied
```

### 原因
Git clone 后脚本默认没有执行权限。

### 解决方案

#### 方案 A: 赋予执行权限（推荐）
```bash
# 进入项目目录
cd skills-health-guardian

# 赋予脚本执行权限
chmod +x scripts/health-check.sh

# 运行
./scripts/health-check.sh --help
```

#### 方案 B: 使用 Python 直接运行（无需权限）
```bash
# 通过 python 运行脚本，无需 chmod
python3 scripts/health-check.sh --help
```

#### 方案 C: 使用 Makefile
```bash
# 如果 Makefile 存在
make scan
```

### 验证
```bash
# 检查权限
ls -l scripts/health-check.sh
# 应该看到: -rwxr-xr-x (可执行)
```

---

## 问题 #4: CLI 命令找不到

### 症状
```bash
python: can't open file '/Users/user/scripts/scanner.py': [Errno 2] No such file or directory
```

### 原因
Python 的搜索路径不包含当前工作目录。

### 解决方案

#### ✅ 正确用法
```bash
# 进入项目根目录
cd skills-health-guardian

# 运行 CLI（相对路径）
python3 scripts/cli.py --help
```

#### ❌ 错误用法
```bash
# 不要使用绝对路径
python3 /full/path/to/skills-health-guardian/scripts/cli.py --help

# 不要在错误目录运行
cd /wrong/directory
python3 ../../skills-health-guardian/scripts/cli.py
```

### 验证
```bash
# 进入项目根目录
cd skills-health-guardian

# 验证当前目录
pwd

# 应该看到类似输出: /path/to/skills-health-guardian
```

---

## 问题 #5: pip install 失败

### 症状
```bash
ERROR: Could not find a version that satisfies the requirement skills-health-guardian
ERROR: No matching distribution found for skills-health-guardian
```

### 原因
Skills Health Guardian **未发布到 PyPI**，不能通过 pip 安装。

### 解决方案

#### ✅ 正确安装方式: Git Clone

```bash
# Clone 仓库
git clone https://github.com/tomansen/skills-health-guardian.git
cd skills-health-guardian

# 直接运行（无需 pip 安装）
python3 scripts/health-check.sh --help
```

#### ✅ 正确安装方式: 下载 ZIP

1. 访问 [GitHub Releases](https://github.com/tomansen/skills-health-guardian/releases)
2. 下载最新版本的 ZIP 文件
3. 解压到任意目录
4. 运行:
   ```bash
   cd skills-health-guardian
   python3 scripts/health-check.sh
   ```

### 未来计划
我们计划在 **v1.1.0** 版本提供 PyPI 支持。关注 GitHub Issues 了解进度。

### 验证
```bash
# 检查项目是否已安装
python3 -c "import skills_health_guardian" 2>&1 && echo "已安装" || echo "未安装（正常，此项目无需 pip 安装）"
```

---

## 问题 #6: Windows 路径分隔符

### 症状
```powershell
FileNotFoundError: [Errno 2] No such file or directory: 'scripts\\scanner.py'
```

### 原因
Windows 使用反斜杠 `\` 作为路径分隔符，但代码可能硬编码了正斜杠 `/`。

### 解决方案

#### PowerShell
```powershell
# Clone 仓库
git clone https://github.com/tomansen/skills-health-guardian.git
cd skills-health-guardian

# 使用反斜杠（PowerShell 自动处理）
python .\scripts\scanner.py --help

# 或者使用正斜杠（PowerShell 也支持）
python ./scripts/scanner.py --help
```

#### CMD
```cmd
git clone https://github.com/tomansen/skills-health-guardian.git
cd skills-health-guardian
python scripts\scanner.py --help
```

#### Git Bash / WSL2
```bash
# Git Bash 自动使用正斜杠
git clone https://github.com/tomansen/skills-health-guardian.git
cd skills-health-guardian
python ./scripts/scanner.py --help
```

### 验证
```powershell
# PowerShell
Test-Path ".\scripts\scanner.py"
# 应该返回: True
```

---

## 问题 #7: 依赖缺失错误

### 症状
```bash
ModuleNotFoundError: No module named 'pathlib'
```

### 原因
Skills Health Guardian 仅依赖 Python 标准库，但某些精简版 Python 发行版可能缺少部分模块。

### 解决方案

#### 检查 Python 安装
```bash
# 验证标准库可用性
python3 -c "import pathlib, json, argparse, sys; print('所有标准库可用')"

# 如果报错，说明 Python 安装不完整
```

#### macOS (使用 Homebrew)
```bash
# 重新安装完整版 Python
brew reinstall python@3.12
```

#### Linux
```bash
# 使用包管理器安装完整版
# Ubuntu/Debian
sudo apt install --reinstall python3.12-minimal

# CentOS/RHEL
sudo yum reinstall python3
```

#### Windows
重新从 [python.org](https://www.python.org/downloads/) 下载完整安装包并重新安装。

### 验证
```bash
python3 -c "import sys; print(f'Python: {sys.version}'); import pathlib; import json; import argparse; print('标准库: OK')"
```

---

## 问题 #8: SKILL.md 不存在错误

### 症状
```bash
ValueError: SKILL.md not found in /path/to/skill
```

### 原因
工具期望每个 skill 都有 SKILL.md 配置文件，但某些 skill 可能没有。

### 解决方案

#### 扫描默认的 skills 目录
```bash
# 不指定 --skill 参数，扫描整个目录
python3 scripts/scanner.py --path ~/.workbuddy/skills

# 或者使用 health-check.sh
./scripts/health-check.sh
```

#### 跳过 SKILL.md 检查
```bash
# 如果测试简单目录，可以跳过元数据检查
python3 scripts/scanner.py --path ./test-skills --skip-skill-md
```

### 验证
```bash
# 检查目标目录
ls ~/.workbuddy/skills

# 应该看到多个 skill 子目录，每个可选包含 SKILL.md
```

---

## 问题 #9: JSON 输出无效

### 症状
```bash
# 使用 Python 解析输出时报错
python3 -c "import json; json.loads('python3 scripts/cli.py --format json')"
ValueError: Expecting value: line 1 column 1 (char 0)
```

### 原因
JSON 输出前可能有警告文本或格式错误。

### 解决方案

#### 使用 --quiet 纯 JSON 模式
```bash
# 添加 --quiet 选项，确保仅输出 JSON
python3 scripts/cli.py --format json --quiet > report.json

# 验证
python3 -c "import json; data = json.load(open('report.json')); print('有效 JSON')"
```

#### 指定输出文件
```bash
# 输出到文件，避免终端文本干扰
python3 scripts/cli.py --format json -o report.json

# 查看
cat report.json | python3 -m json.tool
```

### 验证
```bash
# 生成纯 JSON
python3 scripts/cli.py --format json --quiet > test.json

# 验证 JSON 格式
python3 -m json.tool < test.json > /dev/null && echo "JSON 有效" || echo "JSON 无效"
```

---

## 问题 #10: Docker 构建失败

### 症状
```bash
ERROR [2/5] COPY scripts/ /app/scripts/
---> Error: no such file or directory
```

### 原因
Docker 构建上下文问题，或 .dockerignore 排除了必要文件。

### 解决方案

#### 验证文件存在
```bash
# 确保在项目根目录
cd skills-health-guardian

# 验证
ls scripts/
ls Dockerfile
```

#### 检查 .dockerignore
```bash
# 确保 scripts/ 没有被忽略
cat .dockerignore

# 如果有类似内容，需要删除或修改:
# scripts/
```

#### 正确构建命令
```bash
# 在项目根目录构建
cd skills-health-guardian
docker build -t shg:latest .

# 或者使用 Makefile
make docker-build
```

#### 运行服务
```bash
# CLI 模式
docker run --rm -v $(pwd)/skills:/mnt/skills shg:latest \
    python /app/scripts/scanner.py --path /mnt/skills

# Web Dashboard
docker compose up web

# Cron 模式
docker compose up cron
```

### 验证
```bash
# 验证镜像构建
docker images | grep shg

# 应该看到: shg   latest  <image-id>
```

---

## 🔧 获取更多帮助

### 获取详细帮助
```bash
# Scanner 帮助
python3 scripts/scanner.py --help

# CLI 帮助
python3 scripts/cli.py --help

# Reporter 帮助
python3 scripts/reporter.py --help

# Fixer 帮助
python3 scripts/fixer.py --help
```

### 查看日志
```bash
# 启用详细输出
python3 scripts/cli.py --verbose

# 查看完整的堆栈跟踪
python3 scripts/cli.py --verbose --traceback
```

### 报告新问题
如果上述方案无法解决您的问题，请：

1. **搜索现有 Issues**: [https://github.com/tomansen/skills-health-guardian/issues](https://github.com/tomansen/skills-health-guardian/issues)
2. **创建新 Issue**: 使用模板填写详细信息：
   - 操作系统和版本
   - Python 版本
   - 完整的错误消息
   - 运行的命令
   - 复现步骤

---

## 📞 技术支持

### 获取系统诊断信息

创建 Issue 时，请包含以下诊断信息：

```bash
# 运行诊断命令并复制输出
echo "=== 系统诊断 ===" && \
echo "OS: $(uname -a)" && \
echo "Python: $(python3 --version)" && \
echo "当前目录: $(pwd)" && \
echo "Git 分支: $(git branch --show-current 2>/dev/null || echo 'not a git repo')" && \
echo "=== 完整 ==="
```

### 验证项目完整性

```bash
# 验证所有核心文件存在
ls scripts/scanner.py scripts/reporter.py scripts/fixer.py scripts/health-check.sh scripts/cli.py scripts/platform_utils.py

# 应该看到 7 个文件（新增 platform_utils.py）
```

---

## 问题 #11: 跨平台兼容性（Chrome 检测）

### 症状

**macOS/Linux/Windows 上 Chrome 检测失败**：
```bash
FileNotFoundError: [Errno 2] No such file or directory:
  '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome'
```

### 原因

**v1.0.0 及更早版本** 硬编码了 macOS 特定的 Chrome 路径，导致在 Windows/Linux 上无法检测 Chrome。

### 解决方案

**✅ 已在 v1.0.1 中修复**

跨平台检测模块 `scripts/platform_utils.py` 已自动处理平台差异：

#### 自动检测行为

| 平台 | Chrome 路径检测 |
|------|------------------|
| **macOS** | `/Applications/Google Chrome.app/Contents/MacOS/Google Chrome` |
| **Linux** | `/usr/bin/google-chrome` 或 `/usr/bin/chromium-browser` |
| **Windows** | 自动从 PATH 中查找 `chrome.exe` / `google-chrome.exe` |
| **WSL (Linux)** | 同 Linux，同时识别 WSL 环境 |

#### 验证修复

```bash
# 测试跨平台检测
python3 scripts/platform_utils.py

# 应该看到类似输出：
# === 跨平台工具检测模块测试 ===
# 系统信息:
#   platform: darwin
#   python_version: 3.12.x
#   ...
# Chrome 信息:
#   已安装: True
#   路径: /Applications/Google Chrome.app/Contents/MacOS/Google Chrome
#   版本: 123.0.6312.58
```

#### 如果 Chrome 未检测到

**macOS/Linux**：
```bash
# 确认 Chrome 安装路径
# macOS
ls -la /Applications/Google\ Chrome.app/Contents/MacOS/Google Chrome

# Linux
ls -la /usr/bin/google-chrome
ls -la /usr/bin/chromium-browser
```

**Windows**：
```powershell
# 检查 PATH 是否包含 Chrome
where.exe chrome.exe
where.exe google-chrome.exe

# 如果未找到，需要将 Chrome 安装目录添加到 PATH
```

---

## 问题 #12: 路径分隔符兼容性

### 症状

**Windows 上路径解析错误**：
```powershell
FileNotFoundError: [Errno 2] No such file or directory:
  'scripts\\scanner.py'  # 双反斜杠
```

### 原因

Windows 使用反斜杠 `\` 作为路径分隔符，而 macOS/Linux 使用正斜杠 `/`。

### 解决方案

**✅ 已在 v1.0.1 中修复**

所有代码使用 `pathlib.Path` 自动处理路径分隔符：

```python
from pathlib import Path

# ✅ 正确：跨平台兼容
script_path = Path("scripts") / "scanner.py"
config_dir = Path.home() / ".config" / "app"

# ❌ 错误：硬编码路径分隔符
script_path = "scripts/scanner.py"  # Windows 上可能出问题
```

#### 验证路径处理

```bash
# 测试路径规范化
python3 -c "from scripts.platform_utils import normalize_path; print(normalize_path('~/test'))"

# 输出: /Users/yourname/test  (macOS/Linux)
# 输出: C:\Users\yourname\test  (Windows)
```

---

## 问题 #13: 配置目录位置差异

### 症状

**不同平台下配置文件找不到**：
```bash
FileNotFoundError: [Errno 2] No such file or directory:
  '~/.config/skills-health-guardian'  # macOS 上错误
```

### 原因

不同平台的配置目录规范不同：
- **macOS**: `~/Library/Application Support/`
- **Linux**: `~/.config/`
- **Windows**: `%APPDATA%/`

### 解决方案

**✅ 已在 v1.0.1 中修复**

使用 `platform_utils.get_config_directory()` 获取平台规范的配置目录：

```python
from scripts.platform_utils import get_config_directory

config_dir = get_config_directory("skills-health-guardian")
# macOS: ~/Library/Application Support/skills-health-guardian
# Linux: ~/.config/skills-health-guardian
# Windows: %APPDATA%\skills-health-guardian
```

---

## 🔧 跨平台支持测试

### 运行跨平台测试套件

```bash
# 测试平台检测模块
python3 -m pytest tests/test_platform_utils.py -v

# 测试所有功能
python3 -m pytest tests/ -v

# 仅测试跨平台相关
python3 -m pytest tests/ -k "platform or path" -v
```

### 验证系统信息

```bash
# 查看当前系统诊断
python3 scripts/platform_utils.py
```

---

## 📋 已修复的兼容性问题

| 问题 | 版本 | 状态 |
|------|------|:----:|
| Chrome 检测硬编码 macOS 路径 | v1.0.1 | ✅ 已修复 |
| 路径分隔符跨平台兼容性 | v1.0.1 | ✅ 已修复 |
| 配置目录平台规范差异 | v1.0.1 | ✅ 已修复 |
| Windows CMD/PowerShell 路径处理 | v1.0.1 | ✅ 已修复 |
| WSL 环境检测 | v1.0.1 | ✅ 已支持 |

---

**最后更新**: 2026-04-10  
**文档版本**: 1.0.1  
**相关文档**: [README.md](../README.md) | [Docker Guide](docker-guide.md)
