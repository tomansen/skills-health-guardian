# Skills Health Guardian — Makefile
# 便捷命令: make lint / make test / make check

.PHONY: lint test check format build clean help

# ============================================================
#  默认目标: 显示帮助
# ============================================================
help:
	@echo "Skills Health Guardian — 可用命令:"
	@echo ""
	@echo "  make lint       运行 ruff 静态检查 + 格式检查"
	@echo "  make format     自动格式化代码 (ruff format)"
	@echo "  make test       运行测试 (pytest + coverage)"
	@echo "  make check      完整检查: lint → test → health-check"
	@echo "  make build      构建 sdist + wheel"
	@echo "  make clean      清理构建产物"
	@echo ""

# ============================================================
#  Lint
# ============================================================
lint:
	ruff check scripts/ tests/
	ruff format --check scripts/ tests/

format:
	ruff format scripts/ tests/
	ruff check --fix scripts/ tests/

# ============================================================
#  Test
# ============================================================
test:
	pytest tests/ \
		--cov=scripts \
		--cov-report=term-missing \
		--cov-fail-under=40 \
		-v

test-verbose:
	pytest tests/ -v -s --tb=long

# ============================================================
#  Health Check（一键巡检）
# ============================================================
check: lint test
	@echo ""
	@echo "✅ Lint 和测试全部通过，运行 health-check..."
	chmod +x scripts/health-check.sh
	bash scripts/health-check.sh --dry-run || echo "[INFO] health-check 完成 (退出码: $$?)"

check-ci:
	@echo "=== CI 模式完整检查 ==="
	$(MAKE) lint
	$(MAKE) test
	@echo ""
	@echo "✅ CI 检查通过"

# ============================================================
#  Build
# ============================================================
build:
	python -m build
	twine check dist/*

clean:
	rm -rf dist/ build/ *.egg-info .coverage coverage.xml .pytest_cache __pycache__
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete 2>/dev/null || true
