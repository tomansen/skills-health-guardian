# ============================================================
#  Skills Health Guardian - Docker Image
#  精简构建，基于 Python 3.13 slim
# ============================================================

FROM python:3.13-slim

LABEL maintainer="tomasen <tomansen@163.com>"
LABEL description="Skills Health Guardian - AI Agent Skills Environment Health Monitor"
LABEL version="1.0.0"
LABEL org.opencontainers.image.source="https://github.com/tomansen/skills-health-guardian"

# 构建参数 — 允许覆盖依赖安装
ARG PIP_EXTRA_INDEX_URL=""
ARG INSTALL_DEV=false

# 安装系统依赖（最小集）
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        git \
        bash \
        # scanner.py 需要 subprocess 调用外部工具检测
    && rm -rf /var/lib/apt/lists/* /tmp/* /var/tmp/*

WORKDIR /app

# 先复制依赖声明文件（利用 Docker 缓存层）
COPY pyproject.toml ./

# 从 pyproject.toml 的 dependencies 字段提取并安装
# 当前只有: rich>=13.0
RUN pip install --no-cache-dir --upgrade pip setuptools wheel \
    && if [ -f pyproject.toml ]; then \
        pip install --no-cache-dir $(grep -oP '(?<=").+?(?=")' pyproject.toml | grep -E 'rich|requests|click' || true); \
       fi \
    # 直接安装核心运行时依赖
    && pip install --no-cache-dir "rich>=13.0"

# 复制项目源码
COPY scripts/ ./scripts/
COPY SKILL.md ./

# 创建报告输出目录
RUN mkdir -p /app/reports /app/reports/history

# 环境变量默认值
ENV SKILLS_PATH=/skills \
    REPORT_DIR=/app/reports \
    PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1

# 默认入口：CLI 扫描模式
ENTRYPOINT ["python3", "-m", "scanner"]
CMD ["--help"]
