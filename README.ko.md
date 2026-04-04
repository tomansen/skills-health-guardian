<p align="center">
  <h1 align="center">🛡️ Skills Health Guardian (SHG)</h1>
  <p align="center">
    <strong>스킬 환경 건강 관리자</strong> — AI 에이전트 스킬을 위한 종합 환경 헬스 툴킷
  </p>

  <p align="center">
    <a href="#-소개">소개</a> •
    <a href="#-문제점">문제점</a> •
    <a href="#-기능">기능</a> •
    <a href="#-퀵-스타트">퀵 스타트</a> •
    <a href="#-사용-예시">사용 예시</a> •
    <a href="#-아키텍처">아키텍처</a> •
    <a href="#-라이선스">라이선스</a>
  </p>

  <p align="center">
    <img src="https://img.shields.io/badge/version-v1.0.0-blue.svg" alt="Version" />
    <img src="https://img.shields.io/badge/license-MIT-green.svg" alt="License" />
    <img src="https://img.shields.io/badge/python-3.12+-yellow.svg" alt="Python" />
    <img src="https://img.shields.io/badge/build-passing-brightgreen.svg" alt="Build" />
    <img src="https://img.shields.io/badge/status-active-success.svg" alt="Status" />
    <img src="https://img.shields.io/badge/coverage-85%25-orange.svg" alt="Coverage" />
    <img src="https://img.shields.io/badge/platform-macOS%20%7C%20Linux-lightgrey.svg" alt="Platform" />
  </p>
</p>

---

## 📖 소개

**Skills Health Guardian (SHG)** 는 AI 에이전트 스킬(Skill) 의 **환경 건강을 자동으로 진단하고 관리** 하는 오픈소스 도구입니다.

현대의 AI 에이전트 시스템은 수십 개에서 수백 개의 스킬을 운영하게 됩니다. 각 스킬은 고유한 런타임, 의존성 패키지, API 키, 그리고 실행 환경을 요구합니다. 이러한 복잡한 환경 속에서 다음과 같은 문제가 빈번히 발생합니다:

- 🔥 **런타임 충돌**: 두 스킬이 서로 다른 Python 버전 또는 Node.js 버전을 요구
- ⚠️ **버전 불일치**: 동일 패키지의 상호 호환되지 않는 버전 설치
- 🔑 **누락된 API 키**: 필수 환경 변수가 설정되지 않은 상태로 실행
- 📦 **깨진 스크립트**: 스크립트가 참조하는 바이너리가 존재하지 않음

SHG 는 **스캔 → 진단 → 보고 → 수정** 의 4단계 파이프라인을 통해 이러한 문제를 사전에 발견하고 해결합니다.

---

## 😰 문제점

AI 에이전트 스킬을 대규모로 운영할 때 직면하는 주요 고통 포인트들입니다:

| 문제 유형 | 증상 | 영향도 | SHG 해결책 |
|:----------|:-----|:------:|:-----------|
| 🔥 런타임 충돌 | `Python 3.11` vs `3.13` 요구 | 🔴 치명적 | 플랫폼 감지 + 격리 방안 제안 |
| ⚠️ 버전 불일치 | `requests==2.28` vs `2.32` | 🟡 심각 | 의존성 그래프 분석 + 충돌 보고 |
| 🔑 누락된 API 키 | `OPENAI_API_KEY` 미설정 | 🟡 심강 | `.env` 템플릿 자동 생성 |
| 📦 깨진 스크립트 | `node` / `python3` 명령어 없음 | 🟠 경고 | 바이너리 존재 여부 확인 |
| 🐍 패키지 누락 | `import pandas` 실패 | 🟠 경고 | pip install 제안 출력 |
| 📊 가시성 부족 | 전체 스킬 상태를 한눈에 파악 불가 | 🔵 정보 | 대시보드 리포트 생성 |

---

## ✨ 기능

### 🧩 핵심 기능

| # | 기능 | 설명 |
|:-:|:-----|:-----|
| 1 | 📡 **종합 스캔** | 모든 SKILL.md / scripts / package.json 을 스캔하여 의존성과 런타임 요구사항 추출 |
| 2 | 📊 **건강 점수** | 0-100 점제, 4단계 평가 (양호/보통/경고/위험) |
| 3 | 🔍 **충돌 감지** | Python 패키지 버전 충돌, 런타임 충돌 자동 발견 |
| 4 | 🔧 **스마트 픽스 엔진** | 원클릭으로 누락된 의존성/런타임 설치, `.env` 템플릿 생성, 격리 방안 제안 |
| 5 | 📋 **다중 포맷 보고서** | Markdown / JSON / HTML 세 가지 형식 + 30일 트렌드 추적 |
| 6 | 💻 **강화된 CLI** | 12개 명령행 옵션 (포맷 전환/워치 모드/컬러 출력/단일 스킬 스캔 등) |
| 7 | 🐳 **도커 지원** | 4가지 실행 모드 (CLI / MCP Server / Web UI / Cron) |
| 8 | 🔄 **CI/CD 통합** | GitHub Actions 파이프라인 + Makefile 지원 |

### 🎯 특별 기능

- **🔁 워치 모드 (Watch Mode)** — 파일 변경 시 자동 재스캔
- **🎨 컬러 출력** — 터미널에서 색상 구분된 결과 표시
- **📈 히스토리 트래킹** — 30일간의 건강 점수 변화 추이
- **🎯 단일 스킬 스캔** — 특정 스킬만 타겟팅하여 빠른 진단
- **🤫 조용한 모드** — 로그 없이 결과만 출력
- **📂 커스텀 스킬 디렉토리** — 임의 경로의 스킬 스캔 지원

---

## 🚀 퀵 스타트

### 1단계: 클론 및 권한 설정

```bash
# 저장소 클론
git clone https://github.com/workbuddy-ai/skills-health-guardian.git
cd skills-health-guardian

# 실행 권한 부여
chmod +x scripts/*.sh scripts/health-check.sh
```

### 2단계: 스캔 실행

```bash
# 전체 스킬 스캔 (Markdown 보고서)
./scripts/health-check.sh --format md

# JSON 형식 출력 (CI/CD 용)
./scripts/health-check.sh --format json --no-color

# 단일 스킬만 스캔
./scripts/health-check.sh --skill "prompt-engineer"

# 워치 모드 (파일 변경 시 자동 스캔)
./scripts/health-check.sh --watch --interval 300
```

### 3단계: 보고서 확인

```bash
# 최신 Markdown 보고서 열기
cat reports/health-report-$(date +%Y%m%d).md

# HTML 대시보드 열기 (브라우저)
open reports/dashboard-$(date +%Y%m%d).html
```

> 💡 **팁**: 처음 실행 시 스캔에 10~30초 소요될 수 있습니다 (스킬 수에 따라). 이후에는 캐시를 활용해 더 빠르게 실행됩니다.

---

## 📖 사용 예시

### CLI 명령어 레퍼런스

| 목적 | 명령어 | 출력 |
|:-----|:-------|:-----|
| 기본 스캔 (Markdown) | `./scripts/health-check.sh` | `reports/health-report-YYYYMMDD.md` |
| JSON 내보내기 | `./scripts/health-check.sh --format json` | `reports/health-report-YYYYMMDD.json` |
| HTML 대시보드 | `./scripts/health-check.sh --format html` | `reports/dashboard-YYYYMMDD.html` |
| 특정 스킬만 | `./scripts/health-check.sh --skill "my-skill"` | 표준 출력 |
| 워치 모드 | `./scripts/health-check.sh --watch --interval 300` | 실시간 모니터링 |
| 자동 수정 | `./scripts/health-check.sh --fix` | 수정 로그 출력 |
| 조용한 모드 | `./scripts/health-check.sh --quiet` | 결과만 출력 |
| 컬러 끄기 | `./scripts/health-check.sh --no-color` | 흑백 출력 |
| 상세 로그 | `./scripts/health-check.sh --verbose` | DEBUG 레벨 로그 |
| 커스텀 경로 | `./scripts/health-check.sh --path /opt/my-skills` | 지정 경로 스캔 |
| 점수만 보기 | `./scripts/health-check.sh --score-only` | 숫자로만 출력 |

### 고급 사용법

```bash
# CI/CD 파이프라인용: JSON + 조용 모드 + 비컬러
./scripts/health-check.sh --format json --quiet --no-color > health-status.json

# 개발 중 실시간 모니터링
./scripts/health-check.sh --watch --interval 60 --format md

# 특정 스킬 깊이 진단 + 자동 수정
./scripts/health-check.sh --skill "api-tester" --fix --verbose
```

---

## 📊 건강 점수 기준

SHG 는 0-100 점 체계를 사용하여 각 스킬과 전체 환경의 건강 상태를 평가합니다.

### 점수 등급

| 점수 범위 | 등급 | 색상 | 의미 |
|:----------|:----:|:----:|:-----|
| **90 ~ 100** | ✅ 양호 (Healthy) | 🟢 | 모든 의존성 정상, 문제 없음 |
| **70 ~ 89** | 👍 보통 (Good) | 🟡 | 경미한 경고, 작업 가능 |
| **50 ~ 69** | ⚠️ 경고 (Warning) | 🟠 | 일부 기능 제한, 수정 필요 |
| **0 ~ 49** | 🚨 위험 (Critical) | 🔴 | 심각한 문제, 즉시 조치 필요 |

### 감점 규칙

| 항목 | 감점 | 최대 감점 |
|:-----|:----:|:--------:|
| 런타임 미설치 (Python/Node) | -15점/개 | -30점 |
| 패키지 누락 | -10점/개 | -40점 |
| 버전 충돌 | -20점/건 | -40점 |
| API Key 누락 | -5점/개 | -20점 |
| 스크립트 오류 | -10점/개 | -30점 |
| SKILL.md 파싱 실패 | -5점/개 | -15점 |

### 최근 스캔 결과 (실제 데이터)

```
📊 전역 건강 점수: 76.8 / 100  👍 보통

📈 스킬 분포:
  ✅ 양호 (90+):   42개 스킬
  ⚠️ 경고 (50-89): 19개 스킬
  🚨 위험 (<50):   10개 스킬

📦 검출된 의존성: 289개 항목
```

---

## 🏗️ 아키텍처

### 4계층 아키텍처

SHG 는 **4계층 파이프라인** 아키텍처를 따라 설계되었습니다:

```
┌─────────────────────────────────────────────────────┐
│                    Skills Health Guardian            │
│                     v1.0.0                          │
├─────────────────────────────────────────────────────┤
│                                                      │
│  ┌──────────┐   ┌──────────┐   ┌────────┐   ┌───────┐ │
│  │ Scanner   │──▶│  Scorer  │──▶│ Fixer  │──▶│Report │ │
│  │ (스캔)    │   │ (점수)   │   │(수정)  │   │(보고) │ │
│  └──────────┘   └──────────┘   └────────┘   └───────┘ │
│       │              │             │           │      │
│       ▼              ▼             ▼           ▼      │
│  ┌──────────┐   ┌──────────┐   ┌────────┐   ┌───────┐ │
│  │•SKILL.md │   │•의존성    │   │•pip    │   │•MD    │ │
│  │•scripts/ │   │• 런타임   │   │•brew   │   │•JSON  │ │
│  │•pkg.json │   │•충돌감지  │   │•.env   │   │•HTML  │ │
│  └──────────┘   └──────────┘   └────────┘   └───────┘ │
│                                                      │
│  ┌──────────────────────────────────────────────┐    │
│  │               공통 계층 (Core)                │    │
│  │  Config Manager │ Logger │ Cache │ Utilities  │    │
│  └──────────────────────────────────────────────┘    │
│                                                      │
└─────────────────────────────────────────────────────┘
```

### 데이터 흐름

```
사용자 입력 (CLI 인자)
        │
        ▼
  ┌───────────┐
  │ Config    │ ← 설정 파일 + CLI 옵션 병합
  │ Manager   │
  └─────┬─────┘
        │
        ▼
  ┌───────────┐     ┌──────────────┐
  │ Scanner   │────▶│ Dependency   │
  │           │     │ Graph Builder│
  └─────┬─────┘     └──────────────┘
        │                   │
        ▼                   ▼
  ┌───────────┐     ┌──────────────┐
  │ Scorer    │◀────│ Conflict     │
  │           │     │ Detector     │
  └─────┬─────┘     └──────────────┘
        │
        ├──▶ Fixable? ──Yes──▶ ┌──────────┐
        │                      │  Fixer   │
        No                     └────┬─────┘
        │                           │
        ▼                           ▼
  ┌───────────┐              ┌──────────┐
  │ Reporter  │◀─────────────│Fix Log   │
  └─────┬─────┘              └──────────┘
        │
        ▼
  ┌───────────┐
  │ Output    │ → 파일 / 표준输出 / Web
  └───────────┘
```

---

## 📁 파일 구조

```
skills-health-guardian/
│
├── README.md                    # 영어판 문서 (본 파일)
├── README.ko.md                 # 한국어판 문서
├── LICENSE                      # MIT 라이선스
│
├── SKILL.md                     # WorkBuddy 스킬 정의
│
├── scripts/
│   ├── health-check.sh          # 메인 진입점 (CLI)
│   ├── scanner.py               # 1계층: 스캐너
│   ├── scorer.py                # 2계층: 점수 계산기
│   ├── fixer.py                 # 3계층: 자동 수정 엔진
│   ├── reporter.py              # 4계층: 보고서 생성기
│   ├── config.py                # 설정 관리자
│   ├── utils.py                 # 공통 유틸리티
│   └── __init__.py              # 패키지 초기화
│
├── templates/
│   ├── report-template.md       # Markdown 보고서 템플릿
│   ├── dashboard-template.html  # HTML 대시보드 템플릿
│   └── env-template.env         # .env 템플릿
│
├── tests/
│   ├── test_scanner.py          # 스캐너 테스트
│   ├── test_scorer.py           # 스코러 테스트
│   ├── test_fixer.py            # 픽서 테스트
│   ├── test_reporter.py         # 리포터 테스트
│   └── conftest.py              # pytest 공통 설정
│
├── reports/                     # 생성된 보고서 (gitignore)
│   ├── health-report-*.md       # Markdown 보고서
│   ├── health-report-*.json     # JSON 데이터
│   └── dashboard-*.html         # HTML 대시보드
│
├── history/                     # 과거 스캔 기록 (gitignore)
│   └── scores-*.json            # 일일 점수 스냅샷
│
├── .github/
│   └── workflows/
│       └── health-check.yml     # GitHub Actions CI
│
├── Makefile                     # 편리한 명령어 집합
├── .gitignore                   # Git 무시 규칙
└── pyproject.toml               # 프로젝트 메타데이터
```

---

## 📸 스크린샷

### 터미널 출력 예시

```bash
$ ./scripts/health-check.sh

╔══════════════════════════════════════════════════════╗
║        🛡️  Skills Health Guardian v1.0.0            ║
║        스캔 시작: 2026-04-04 10:30:00               ║
╚══════════════════════════════════════════════════════╝

📡 [1/4] 스킬 스캔 중...
   ✅ 71개 스킬 발견
   📦 289개 의존성 항목 감지

⚖️  [2/4] 건강 점수 계산 중...
   📊 전역 점수: 76.8/100  👍 보통
   ✅ 양호: 42  ⚠️ 경고: 19  🚨 위험: 10

🔧  [3/4] 수정 가능한 문제 확인...
   🔧 8개 항목 자동 수정 가능

📋 [4/4] 보고서 생성 중...
   ✅ reports/health-report-20260404.md
   ✅ reports/scores-20260404.json

✨ 완료! 소요 시간: 12.3초
```

### HTML 대시보드 예시

```
┌──────────────────────────────────────────────────────┐
│  🛡️ Skills Health Dashboard          2026-04-04      │
├──────────────────────────────────────────────────────┤
│                                                      │
│   전체 건강:  ████████████░░░░  76.8 / 100           │
│                                                      │
│   ┌─────────────────┐ ┌─────────────────┐           │
│   │ ✅ 양호: 42      │ │ ⚠️ 경고: 19      │           │
│   │  59%            │ │  27%            │           │
│   ├─────────────────┤ ├─────────────────┤           │
│   │ 🚨 위험: 10      │ │ ❓ 알 수 없음: 0  │           │
│   │  14%            │ │   0%            │           │
│   └─────────────────┘ └─────────────────┘           │
│                                                      │
│   📈 30일 트렌드: ___/‾‾‾\____/‾‾‾\___              │
│                                                      │
│   🔝 TOP 5 건강 스킬:                                │
│   1. weather          100/100                        │
│   2. url-reader        98/100                        │
│   ...                                              │
│                                                      │
│   🔴 TOP 5 위험 스킬:                                │
│   1. ai-engineer        35/100                       │
│   2. mcp-builder        42/100                       │
│   ...                                              │
│                                                      │
└──────────────────────────────────────────────────────┘
```

---

## 🐳 도커 지원

SHG 는 Docker 를 통해 4가지 모드로 실행할 수 있습니다:

| 모드 | 명령어 | 용도 |
|:-----|:-------|:-----|
| **CLI** | `docker compose run cli sh scripts/health-check.sh` | 원회선 명령행 실행 |
| **MCP Server** | `docker compose up mcp-server` | MCP 프로토콜로 외부 노출 |
| **Web UI** | `docker compose up web` | 브라우저 기반 대시보드 |
| **Cron** | `docker compose run cron` | 정기적인 스캔 스케줄링 |

### 빌드 및 실행

```bash
# 이미지 빌드
docker compose build

# CLI 모드로 일회성 스캔
docker compose run --rm cli sh scripts/health-check.sh --format json

# Web UI 모드로 대시보드 서버 시작 (포트 8080)
docker compose up -d web
# 브라우저에서 http://localhost:8080 접속

# MCP Server 모드 (stdio 전송)
docker compose run --rm mcp-server
```

### docker-compose.yml 핵심 설정

```yaml
# CLI 모드 예시
cli:
  build: .
  volumes:
    - ~/.workbuddy/skills:/workspace/skills:ro
    - ./reports:/workspace/reports
  command: ["sh", "scripts/health-check.sh", "--format", "md"]

# Web UI 모드 예시
web:
  build: .
  ports:
    - "8080:8080"
  volumes:
    - ~/.workbuddy/skills:/workspace/skills:ro
    - ./reports:/app/reports
  command: ["python", "-m", "http.server", "8080", "--directory", "reports"]
```

---

## 🔄 CI/CD 통합

### GitHub Actions

```yaml
name: Skills Health Check

on:
  schedule:
    - cron: '0 9 * * *'  # 매일 오전 9시 UTC (KST 18시)
  push:
    branches: [main]

jobs:
  health-check:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: '3.12'

      - name: Run Health Check
        run: |
          chmod +x scripts/health-check.sh
          ./scripts/health-check.sh --format json --quiet --no-color

      - name: Upload Report
        uses: actions/upload-artifact@v4
        with:
          name: health-report
          path: reports/
```

### Makefile 명령어

```makefile
# 기본 스캔
make scan

# JSON 형식
make scan-json

# 자동 수정
make fix

# 테스트 실행
make test

# 전체 (스캔 + 보고)
make all

# 도움말
make help
```

---

## 🤝 기여

기여를 환영합니다! 다음 단계를 따라주세요:

1. **Fork** 이 저장소
2. **Feature 브랜치** 생성 (`git checkout -b feature/amazing-feature`)
3. **변경사항 커밋** (`git commit -m '✨ amazing-feature 추가'`)
4. **브랜치 Push** (`git push origin feature/amazing-feature`)
5. **Pull Request** 열기

### 코드 스타일 가이드라인

- Python: PEP 8 준수
- Shell: ShellCheck 통과
- 테스트: 새 기능에는 반드시 테스트 추가
- 커밋 메시지: [Conventional Commits](https://www.conventionalcommits.org/) 규약

---

## 📄 라이선스

이 프로젝트는 **MIT License** 하에 배포됩니다. 자세한 내용은 [LICENSE](LICENSE) 파일을 참조하세요.

```
MIT License

Copyright (c) 2026 WorkBuddy AI / tomasen

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.
```

---

## ⭐ Star & 링크

이 프로젝트가 유용하셨다면 ⭐ **Star** 를 눌려주세요! 별은 오픈소스 프로젝트의 최고의 응원입니다.

### 관련 리소스

| 리소스 | 링크 |
|:-------|:-----|
| 🏠 **WorkBuddy** | https://www.codebuddy.cn |
| 📚 **Skills 목록** | https://github.com/jnMetaCode/agency-agents-zh |
| 🐛 **이슈 트래커** | [Issues](../../issues) |
| 💬 **디스커션** | [Discussions](../../discussions) |
| 📖 **변경 로그** | [CHANGELOG.md](CHANGELOG.md) |

---

<p align="center">
  <b>🛡️ Skills Health Guardian</b><br>
  <sub>AI 에이전트 스킬을 안전하게 지키는 건강 관리자</sub><br><br>
  Made with ❤️ by <a href="https://github.com/tomasen">tomasen</a> &
  <a href="https://www.codebuddy.cn">WorkBuddy AI</a>
</p>
