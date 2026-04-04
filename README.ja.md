# 🛡️ Skills Health Guardian (SHG)

<p align="center">
  <img src="https://img.shields.io/badge/version-v1.0.0-blue" alt="Version" />
  <img src="https://img.shields.io/badge/license-MIT-green" alt="License" />
  <img src="https://img.shields.io/badge/python-3.12%2B-yellow" alt="Python" />
  <img src="https://img.shields.io/badge/platform-macOS%20%7C%20Linux-lightgrey" alt="Platform" />
  <img src="img.shields.io/badge/status-stable-brightgreen" alt="Status" />
  <img src="https://img.shields.io/badge/dependencies-zero-success" alt="Zero Dependencies" />
  <img src="https://img.shields.io/badge/score-76.8%2F100-orange" alt="Health Score" />
</p>

---

<p align="center">
  <strong>スキル環境・ヘルス・ガーディアン</strong><br />
  スキャン → 診断 → レポート → 修正 — AIエージェントスキルのための包括的な環境ヘルスツールキット
</p>

---

## 📖 概要

**Skills Health Guardian (SHG)** は、AI エージェントの Skill 環境を包括的に監視・診断・修復するためのコマンドラインツールです。71 個以上のスキル、289 個の依存項目を瞬時にスキャンし、競合検出から自動修正までをワンストップで提供します。

現代の AI エージェント開発では、数十〜数百個の Skill（スキル）が協調して動作します。各スキルは異なるランタイム、依存関係、環境変数を必要とし、それらが複雑に絡み合うことで以下のような問題が頻発します：

- 🔥 **ランタイム競合**: Python 3.11 必要なスキルと Node.js 18 必要なスキルが共存
- ⚠️ **バージョンの不一致**: 同一パッケージの互換しないバージョンが混在
- 🔑 **欠落した API キー**: 環境変数が未設定でスキルが機能不全
- 🐛 **スクリプトエラー**: 依存関係がインストールされていないため実行時クラッシュ

SHG はこれらの課題を **4 層アーキテクチャ**（Scanner → Scorer → Fixer → Reporter）で体系的に解決し、チーム全体のスキル環境を可視化・正常化します。

## 😰 解決する課題

| 課題 | 影響 | SHG の解決策 |
|------|------|--------------|
| ランタイム競合 | スキルが起動できない | 自動検出 + 分離方案提案 |
| バージョンの不一致 | 予期せぬ動作やエラー | 依存グラフ解析 + 推奨バージョン提示 |
| 欠落した API キー | 機能制限や認証エラー | `.env` テンプレート自動生成 |
| 未インストール依存関係 | 実行時エラー | ワンクリック自動インストール |
| 環境の不透明性 | 問題特定に時間がかかる | 0-100 点数制で一目で把握 |
| 大規模展開時の管理困難 | 手作業では追いつけない | CI/CD 統合 + 定期自動スキャン |

## ✨ 主な機能

| 機能 | 説明 |
|------|------|
| 🔍 **包括的スキャン** | 全ての `SKILL.md` / `scripts/` / `package.json` を走査し、依存関係とランタイム要件を抽出 |
| 📊 **ヘルススコアリング** | 0-100 点数制で評価、4 段階の健全性レベル（健全 / 良好 / 警告 / 危険） |
| ⚡ **競合検出** | Python パッケージバージョン競合、ランタイム競合を自動検出してレポート |
| 🔧 **スマートフィックス** | 不足依存关系のインストール、`.env` テンプレート生成、分離方案の提案 |
| 📝 **マルチフォーマットレポート** | Markdown / JSON / HTML の 3 形式で出力 + 30 日間トレンド追跡対応 |
| 🖥️ **強化された CLI** | 12 個のコマンドラインオプション（フォーマット切替 / ウォッチモード / カラー出力等） |
| 🐳 **Docker サポート** | CLI / MCP / Web / Cron の 4 つの実行モードに完全対応 |
| 🔄 **CI/CD 統合** | GitHub Actions ワークフロー + Makefile で DevOps パイプラインに組み込み可能 |

## 🚀 クイックスタート

### ステップ 1: インストール

```bash
# リポジトリをクローン
git clone https://github.com/your-org/skills-health-guardian.git
cd skills-health-guardian

# 実行権限付与
chmod +x scripts/health-check.sh
```

### ステップ 2: 初回スキャン実行

```bash
# 基本スキャン（全スキル対象）
./scripts/health-check.sh --scan

# 特定のスキルのみスキャン
./scripts/health-check.sh --scan --skill "frontend-developer"
```

### ステップ 3: レポートを確認

```bash
# Markdown レポートで結果を表示
./scripts/health-check.sh --report --format md

# HTML ダッシュボードで視覚化
./scripts/health-check.sh --report --format html --output ./reports/
```

## 📋 使用例

### CLI コマンド一覧

| コマンド | 説明 | 例 |
|----------|------|-----|
| `--scan` | 全スキルをスキャン | `./health-check.sh --scan` |
| `--skill <name>` | 単一スキルを指定 | `--skill "code-reviewer"` |
| `--format <fmt>` | 出力形式を選択 | `--format json\|md\|html` |
| `--output <dir>` | 出力ディレクトリ指定 | `--output ./reports/` |
| `--watch` | ウォッチモード（継続監視） | `--watch --interval 300` |
| `--color` | カラー出力有効化 | `--color` |
| `--fix` | 自動修正モード | `--fix --auto` |
| `--trend` | 30 日間トレンド表示 | `--trend` |
| `--quiet` | シンプル出力 | `--quiet` |
| `--verbose` | 詳細デバッグ出力 | `--verbose` |
| `--help` | ヘルプ表示 | `--help` |
| `--version` | バージョン情報 | `--version` |

### 実運用例

```bash
# 🔍 定期ヘルスチェック（Cron 用）
./scripts/health-check.sh --scan --format json --output /var/log/shg/ --quiet

# 🔧 問題のあるスキルを自動修正
./scripts/health-check.sh --scan --fix --auto --format md

# 📊 HTML ダッシュボード生成
./scripts/health-check.sh --scan --report --format html --output ./dashboard/

# 👁️ 継続監視モード（5 分間隔）
./scripts/health-check.sh --watch --interval 300 --color
```

## 📈 ヘルススコア基準

### 評価レベル

| スコア範囲 | レベル | 色 | 説明 |
|-----------|--------|-----|------|
| **90 - 100** | 🟢 健全 (Healthy) | 緑 | 全てのスキルが正常に動作可能 |
| **70 - 89** | 🟡 良好 (Good) | 黄 | 軽微な警告あり、機能に影響なし |
| **50 - 69** | 🟠 警告 (Warning) | オレンジ | 一部スキルに問題あり、修正推奨 |
| **0 - 49** | 🔴 危険 (Dangerous) | 赤 | 複数スキルが機能不全、即時対応必要 |

### 減点ルール

| 項目 | 減点 | 条件 |
|------|------|------|
| ランタイム未検出 | -5 / スキル | SKILL.md に runtime セクションがない場合 |
| 依存関係未記載 | -3 / スキル | dependencies セクションが空または不存在 |
| Python バージョン競合 | -10 / 競合 | 同一パッケージの非互換バージョンが存在 |
| API キー未設定 | -8 / キー | 必須環境変数が `.env` にない |
| スクリプト実行不可 | -15 / スキル | scripts/ 内のファイルに実行権限がない |
| 外部依存関係未インストール | -5 / 項目 | requirements.txt の内容がシステムに存在しない |

### 最新スキャン結果（初回）

```
📊 Skills Health Report — 2026-04-04
═══════════════════════════════════════

🎯 グローバルヘルススコア:  76.8 / 100  [良好]
📦 スキャン済みスキル総数:    71 個
✅ 健全:                     42 個 (59.2%)
⚠️  警告:                     19 個 (26.8%)
🔴 危険:                     10 個 (14.1%)

📋 依存項目総数:             289 個
🔧 修正可能項目:              -- 個
```

## 🏗️ アーキテクチャ

```
┌─────────────────────────────────────────────────────────────┐
│                    Skills Health Guardian v1.0.0            │
│                         (4-Layer Architecture)               │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│   ┌─────────────┐                                           │
│   │  🖥️  CLI     │   health-check.sh (Entry Point)          │
│   │  Interface  │   12 options, 4 formats, watch mode       │
│   └──────┬───────┘                                           │
│          │                                                   │
│   ┌──────▼───────┐    ┌─────────────┐                       │
│   │  🔍 Scanner  │───▶│  📊 Scorer  │                       │
│   │             │    │             │                        │
│   │ • SKILL.md  │    │ • 0-100 score                      │
│   │ • scripts/  │    │ • 4-level rating                   │
│   │ • pkg.json  │    │ • Deduction rules                  │
│   └─────────────┘    └──────┬──────┘                       │
│                             │                               │
│          ┌──────────────────┼──────────────────┐            │
│          ▼                  ▼                  ▼            │
│   ┌─────────────┐   ┌─────────────┐   ┌─────────────┐      │
│   │  🔧 Fixer   │   │  📝 Reporter│   │  💾 Storage │      │
│   │             │   │             │   │             │      │
│   │ • Auto-fix  │   │ • Markdown  │   │ • JSON DB   │      │
│   │ • .env gen  │   │ • JSON      │   │ • Trends    │      │
│   │ • Isolation │   │ • HTML      │   │ • History   │      │
│   └─────────────┘   └─────────────┘   └─────────────┘      │
│                                                              │
├─────────────────────────────────────────────────────────────┤
│  Dependencies: Zero (Python Standard Library Only)           │
│  Platform: macOS / Linux (Windows via WSL)                   │
└─────────────────────────────────────────────────────────────┘
```

## 📁 ファイル構造

```
skills-health-guardian/
│
├── README.ja.md                          # 日本語README（本ファイル）
├── README.md                             # 英語README
├── LICENSE                               # MITライセンス
├── SKILL.md                              # WorkBuddy Skill 定義
│
├── scripts/                              # コアスクリプト群
│   ├── health-check.sh                   # メインエントリーポイント
│   ├── scanner.py                        # 依存関係・ランタイムスキャナー
│   ├── scorer.py                         # ヘルススコア計算エンジン
│   ├── fixer.py                          # 自動修正エンジン
│   ├── reporter.py                       # レポートジェネレーター
│   └── utils.py                          # 共通ユーティリティ関数
│
├── templates/                            # テンプレートファイル
│   ├── env.template                      # .env テンプレート
│   ├── report-md.template                # Markdown レポートテンプレート
│   └── report-html.template              # HTML ダッシュボードテンプレート
│
├── config/                               # 設定ファイル
│   ├── scoring-rules.json                # スコアリングルール定義
│   ├── detection-patterns.json           # 検出パターン設定
│   └── ignore-list.json                  # スキャン除外リスト
│
├── data/                                 # データ格納ディレクトリ
│   ├── scans/                            # スキャン結果履歴
│   ├── trends/                           # トレンドデータ（30 日分）
│   └── cache/                            # スキャンキャッシュ
│
├── tests/                                # テストコード
│   ├── test_scanner.py                   # スキャナーテスト
│   ├── test_scorer.py                    # スコーラーテスト
│   ├── test_fixer.py                     # フィッサーテスト
│   └── test_reporter.py                  # レポーターテスト
│
├── docker/                               # Docker 関連ファイル
│   ├── Dockerfile                        # Docker イメージ定義
│   ├── docker-compose.yml                # マルチコンテナ構成
│   └── entrypoint.sh                     # コンテナエントリーポイント
│
├── .github/                              # CI/CD 設定
│   └── workflows/
│       └── health-check.yml              # GitHub Actions ワークフロー
│
├── Makefile                              # DevOps タスク管理
└── pyproject.toml                        # プロジェクトメタデータ
```

## 🖼️ スクリーンショット

<!-- 
TODO: スクリーンショット追加予定

1. **ターミナル出力例**
   - `--scan --color` によるカラー付きスキャン結果
   - ASCII アートによる進捗バーとスコア表示
   
2. **HTML ダッシュボード**
   - ダークテーマのインタラクティブダッシュボード
   - スキル別ヘルススコアの円グラフ・棒グラフ
   
3. **トレンドグラフ**
   - 30 日間のヘルススコア推移
   - 改善・悪化の傾向分析
-->

> 📸 スクリーンショットは近日公開予定です。現在は `--scan --color` を実行してターミナルでご確認ください。

## 🐳 Docker サポート

SHG は Docker を使って 4 つの異なるモードで実行できます。

```bash
# ビルド
docker build -t shg:latest -f docker/Dockerfile .
```

### 実行モード

| モード | コマンド | 説明 |
|-------|---------|------|
| **CLI** | `docker run --rm -v ~/.workbuddy:/data shg:latest --scan` | 通常の CLI スキャン |
| **MCP Server** | `docker run --rm -p 3000:3000 shg:latest --mcp` | MCP サーバーとして起動 |
| **Web Dashboard** | `docker run --rm -p 8080:8080 shg:latest --web` | Web UI ダッシュボード |
| **Cron Job** | `docker run --rm -v /var/log:/logs shg:latest --cron` | 定期スケジュール実行 |

### Docker Compose（フルセット）

```yaml
# docker-compose.yml
services:
  shg-cli:
    build: .
    command: ["--scan", "--format", "json"]
    volumes:
      - ~/.workbuddy:/workspace
      - ./data/reports:/app/output
  
  shg-web:
    build: .
    command: ["--web"]
    ports:
      - "8080:8080"
    volumes:
      - ./data:/app/data
```

```bash
# 全サービス起動
docker compose up -d

# Web ダッシュボードにアクセス
open http://localhost:8080
```

## 🔄 CI/CD 統合

### GitHub Actions

SHG は GitHub Actions と簡単に統合でき、PR ごとやスケジュール実行で自動的にスキルのヘルスチェックを行えます。

```yaml
# .github/workflows/health-check.yml
name: Skills Health Check

on:
  push:
    paths:
      - '.workbuddy/skills/**/SKILL.md'
  schedule:
    - cron: '0 9 * * *'        # 毎日 09:00 UTC 実行
  workflow_dispatch:           # 手動実行も可能

jobs:
  health-check:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      
      - name: Run SHG Scan
        run: |
          chmod +x ./.workbuddy/skills/skills-health-guardian/scripts/health-check.sh
          ./.workbuddy/skills/skills-health-guardian/scripts/health-check.sh \
            --scan \
            --format md \
            --output ./health-reports/
      
      - name: Upload Report
        uses: actions/upload-artifact@v4
        with:
          name: health-report
          path: ./health-reports/
      
      - name: Health Gate  # スコア閾値チェック
        run: |
          SCORE=$(grep 'グローバルヘルススコア' ./health-reports/report.md | grep -oE '[0-9]+\.?[0-9]*')
          echo "Health Score: $SCORE"
          if (( $(echo "$SCORE < 60" | bc -l) )); then
            echo "::warning::Health score $SCORE is below threshold (60)"
          fi
```

### Makefile タスク

```makefile
.PHONY: scan report fix test clean docker

scan:                           ## 全スキルをスキャン
	@./scripts/health-check.sh --scan --color

report:                        ## Markdown レポートを生成
	@./scripts/health-check.sh --scan --report --format md

fix:                           ## 安全な自動修正を実行
	@./scripts/health-check.sh --scan --fix

test:                          ## テストスイートを実行
	@python3 -m pytest tests/ -v

clean:                         ## キャッシュと古いレポートを削除
	@rm -rf data/cache/* data/scans/*

docker-build:                  ## Docker イメージをビルド
	@docker build -t shg:latest .

docker-run:                    ## Docker でスキャン実行
	@docker run --rm -v ${HOME}/.workbuddy:/data shg:latest --scan
```

```bash
# 使い方
make scan         # スキャン実行
make report       # レポート生成
make fix          # 自動修正
make test         # テスト実行
make docker-run   # Docker で実行
```

## 🤝 貢献のご案内

貢献を歓迎します！以下の手順でご参加ください。

1. **Fork** このリポジトリ
2. **Feature ブランチ**を作成 (`git checkout -b feature/amazing-feature`)
3. **変更を Commit** (`git commit -m '✨ amazing-feature を追加'`)
4. **Branch に Push** (`git push origin feature/amazing-feature`)
5. **Pull Request** を開く

### 開発環境のセットアップ

```bash
# リポジトリをクローン
git clone https://github.com/your-org/skills-health-guardian.git
cd skills-health-guardian

# Python 仮想環境を作成（テスト用）
python3 -m venv .venv
source .venv/bin/activate

# テスト実行
python3 -m pytest tests/ -v

# リントチェック
shellcheck scripts/health-check.sh
flake8 scripts/
```

### コーディング規約

- Python: PEP 8 準拠
- Shell: ShellCheck パス必須
- コミットメッセージ: Conventional Commits
- 日本語コメント: 技術用語は英語表記を推奨

## 📄 ライセンス

このプロジェクトは [MIT License](LICENSE) の下でライセンスされています。

```
Copyright (c) 2026 tomansen (https://github.com/tomansen)

本ソフトウェアおよび関連文書ファイル（以下「ソフトウェア」と言います）の
コピーを誰でも無償で取得することができます。これには、ソフトウェアのコピーを
使用、複製、変更、結合、掲示、配布、サブラインス、および/または販売する権限、
およびソフトウェアを提供された者がそうすることを許可する権限が含まれますが、
条件として、上記著作権表示および本許諾表示をすべてのコピーまたはソフトウェアの
重要部分に含める必要があります。
```

## ⭐ Star & リンク

もし本项目が役立った場合は、ぜひ ⭐ **Star** をいただけると励みになります！

### 関連リソース

| リンク | 説明 |
|--------|------|
| [WorkBuddy](https://www.workbuddy.cn) | AI エージェントプラットフォーム |
| [Skills Library](https://github.com/jnMetaCode/agency-agents-zh) | WorkBuddy 公開スキル集 |
| [Issue Tracker](../../issues) | バグ報告・機能リクエスト |
| [Discussions](../../discussions) | コミュニティ討論 |

---

<p align="center">
  Made with ❤️ by <a href="https://github.com/tomansen">tomansen</a>
</p>

<p align="center">
  <sub><b>Skills Health Guardian</b> — AI エージェントスキルのための包括的な環境ヘルスツールキット</sub>
</p>
