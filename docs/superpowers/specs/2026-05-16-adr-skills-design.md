# adr-skills 設計

- 日付: 2026-05-16
- ステータス: 設計合意済み（実装計画待ち）
- 成果物: `adr-skills` — ADR を自律的に起草・管理するスキルパッケージ

## 目的

仕様・アーキテクチャに関わる決定が生じたとき、それを ADR (Architecture Decision Record) として**取りこぼさず記録**する。記録には deciders の合意が要るという ADR 本来の性質を尊重し、「機械的処理（エージェント非依存）」と「合意ベースの起草」を明確に分離する。

ADR は Sphinx + MyST で作成・管理する。パッケージは `sphinx-skills` と同じ流儀で構成し、APM (Agent Package Manager) で配布できる（配布は任意）。

## 背景と前提

- 設計は標準的な ADR 運用（Nygard の軽量フォーマット + MADR 系フロントマター、`1 ADR = 1 決定`、Accepted 後は不変、supersede による更新）に沿う。既存プロジェクトの ADR 運用を調査する場合も、**その決定内容・プロジェクト名・パス等は機密として本パッケージに一切持ち込まず**、構造・テンプレート・運用ルールという一般化可能な形式のみを取り込む。
- ADR テンプレートは `docs/superpowers/specs/` の design spec を出典として参照する。superpowers のブレストが生む spec と ADR は構造的に連結している。
- `superpowers` 本体（ブレスト等のスキル）はプラグインキャッシュ内にあり改変しない。

## ベストプラクティス（スキル本文に焼き込み）

ADR の標準的なプラクティス（Nygard / MADR / adr.github.io）を `adr-author` のスキル本文に取り込む。

- `1 ADR = 1 決定`。決定と理由に集中し、実装詳細（ファイル・関数シグネチャ）は書かない。
- Accepted 後の ADR は不変。変更は新しい ADR を起こして supersede する。
- ステータス遷移: `Proposed` → `Accepted` → `Deprecated` / `Superseded`。
- 検討した代替案・却下理由・トレードオフを正直に記録する。
- フロントマターは MADR 系（`adr` / `title` / `status` / `date` / `deciders` / `supersedes` / `superseded_by`）。参照実装に準拠する。
- 出典抜粋は ADR 内に貼り付けて凍結する（動的 include は採用しない）。

## アーキテクチャ：2 層モデル

「自動記録」を 1 つの機構で実現しようとするとエージェント依存になる。責務を 2 層に分離する。

### 第 1 層：決定的な機構（エージェント非依存）— `adr` CLI

純粋な機械的処理のみを担う。文章は書かない。冪等。エラー時はデフォルト値で続行せず例外を送出する。Python 3.13+ 製、`uv` 前提。

| サブコマンド | 役割 |
|---|---|
| `adr new --title T [--from-spec PATH]` | 次番号を採番し `_templates/adr_template.md` を展開して `NNNN-slug.md` を生成。`index.md` の toctree と一覧に登録。`status: Proposed`。 |
| `adr accept <NNNN>` | フロントマターを `Proposed` → `Accepted` に更新し、`index.md` 一覧の節を移動。 |
| `adr supersede <NNNN> --by <MMMM>` | 旧 ADR に `superseded_by`、新 ADR に `supersedes` を相互リンクし、ステータスを更新。旧ファイルは残す（不変性）。 |
| `adr check` | spec に対応する ADR が無いものを列挙する。**生成はしない**（合意原則）。CI や任意の点検で使う。終了コードで未記録の有無を返す。 |
| `adr list` | ADR 一覧とステータスを表示。 |

どのコーディングエージェント（claude / codex / copilot 等）で作業しても、CLI の挙動は完全に同一になる。

### 第 2 層：起草（人間またはエージェント）— `adr-author` スキル

スタブの中身（Context / Decision / Consequences / Alternatives）を spec を読んで起草する。本質的に推論が要るためエージェントまたは人間の仕事。エージェント差は「呼びかけの精度」と「文章の質」に限定され、第 1 層の正しさには影響しない。

## 成果物の構成

```
adr-skills/
├── apm.yml                       # APM 配布メタデータ（package_type: skill_bundle）
├── pyproject.toml                # CLI 開発用（ruff / mypy / pytest）
├── uv.lock
├── README.md
├── LICENSE
├── skills/
│   ├── adr-init/
│   │   ├── SKILL.md
│   │   ├── tool/adr/             # adr CLI 本体（正典・APM で同梱配布される）
│   │   └── templates/            # conf.py / index.md / adr_template.md / Makefile / make.bat
│   └── adr-author/
│       └── SKILL.md
├── tests/                        # CLI の TDD テスト（配布対象外・CI で実行）
└── .github/workflows/            # lint / test / skill 検証
```

### APM 配布の制約（調査結果）

APM は `package_type: skill_bundle` として `skills/<name>/` 配下のみをエージェントのスキルディレクトリ（`.claude/skills/` 等）へコピー配置する。リポジトリ全体は `~/.apm/apm_modules/` にキャッシュされるが配置対象外。

したがって **CLI とテンプレートは `skills/adr-init/` の中に同梱**する。`src/` 直下に置くと配布時にスキルと一緒に届かない。

## コンポーネント詳細

### `adr` CLI（`skills/adr-init/tool/adr/`）

- 状態とロジックを分離する。フロントマター・`index.md` の読み書きをコントラクトとして厳密に扱う。
- `index.md` への登録は冪等（既に登録済みなら何もしない）。
- 採番は既存 `NNNN-*.md` を走査して最大値 +1。4 桁ゼロ埋め。
- 不正な状態遷移（例: 存在しない ADR の accept、Accepted を再 accept）は例外送出。

### `adr-init` スキル

対象リポジトリに ADR 用 Sphinx プロジェクトを生成する。

- 配置先ディレクトリを決定する。既定は `docs/adr/`（adr.github.io 推奨の標準。superpowers の `docs/superpowers/specs/` と同じ `docs/` ツリーに隣接する）。自動検出: `references/` 系の分類ディレクトリが既にあれば `references/adr/`。ユーザー指定で上書き可。
- `templates/` から `conf.py` / `index.md` / `_templates/adr_template.md` / `Makefile` / `make.bat` / `_static/` を配置する。ADR 用 Sphinx の標準構成（`myst_parser` + `sphinx_oceanid` + `shibuya` テーマ + 日本語 LaTeX）。
- 同梱 CLI を利用側リポジトリの ADR ディレクトリ配下 `_tool/adr/` へ vendoring する。生成する `Makefile` に `adr` 実行用の便宜ターゲットを追加する。以後 `adr-author` は利用側リポジトリにある `_tool/adr/` を `uv run python -m adr` 形式で呼ぶ。CLI が ADR ディレクトリと一緒にバージョン管理されるため、APM 経由でもどのエージェントでも同じ CLI が確実に届く。
- Sphinx のビルド・テーマ運用は `sphinx-skills` をソフト参照（README で案内、ハード依存にしない）。
- 発火条件（description）: 「ADR 管理を始めたい」「ADR を初期化」等。

### `adr-author` スキル

中核。仕様・アーキテクチャに関わる決定が生じた場面で発火し、合意の上で ADR を記録する。

**発火条件（description 設計）**

- 発火する: superpowers の spec (`docs/superpowers/specs/*-design.md`) が書かれた直後 / アーキテクチャに関わる選択（フレームワーク・ライブラリ・境界・プロトコル・データ構造の選定で**代替案を伴う**もの）が確定した場面 / 明示依頼「ADR を書いて」。
- 発火しない（除外）: バグ修正・リファクタリング・ドキュメント更新・UI 微調整など決定を伴わない作業。

**ワークフロー**

1. 決定を抽出する。1 つの spec から複数 ADR 候補が出ることを許容する（1 つの設計判断が複数の独立した決定を含むことは珍しくないため）。
2. 各候補について Context / Decision / Consequences / Alternatives を起草し、spec の該当箇所を抜粋して凍結する。
3. **ユーザーに提示する**:「次の決定を ADR-NNNN としてこう記録します」とプレビューを示し、ADR 化の要否も含めて合意を取る。
4. 合意後、利用側リポジトリの `adr new` でファイルを実体化する（`status: Proposed`）。
5. supersede・Accepted 昇格も同手順（提示 → 合意 → `adr supersede` / `adr accept`）。`Accepted` への昇格は人間の別判断であり、スキルが自動で行わない。

発火条件（description）: 上記「発火条件」を参照。

## データフロー

```
superpowers ブレスト
  └─ docs/superpowers/specs/YYYY-MM-DD-*-design.md を生成
       │
       ▼
adr-author スキル（発火）
  ├─ spec から決定を抽出（1 spec → N ADR 候補）
  ├─ Context/Decision/Consequences/Alternatives を起草
  ├─ ユーザーに提示し合意を取る  ◀── 合意ゲート（必須）
  └─ adr new --from-spec <spec>  ──▶ adr CLI（第 1 層）
                                       ├─ NNNN-slug.md 生成（status: Proposed）
                                       └─ index.md の toctree / 一覧に登録
       │
       ▼
ユーザーレビュー → 合意 → adr accept <NNNN>（別判断・別操作）
```

`adr check` は spec と ADR の対応を点検し、未記録を**列挙のみ**する（黙って生成しない）。CI や任意点検での安全網。

## 「自動記録」の意味（合意済みの定義）

- ✕ 黙ってファイルを自動生成する。
- ○ アーキテクチャ・仕様に関わる決定を**取りこぼさず検知して提案**し、deciders の合意の上で記録する。合意ステップは ADR の本質そのもの。
- エージェント非依存性は 2 箇所で担保する。(1) 機械処理（採番・index 登録・status・supersede）は CLI に寄せて完全同一挙動。(2) 取りこぼしは `adr check` で事後検出できる。

## エラー処理方針

- フォールバック禁止。CLI はエラー時にデフォルト値で続行せず例外を送出する。
- `adr-author` は ADR プロジェクト未初期化（`adr` コマンド不在）を検知したら、暗黙に進めず「先に `adr-init` を実行してください」と明示する。
- 不正な状態遷移は CLI が拒否し、理由を明示する。

## 機密保持（不変条件）

- スキルパッケージ（`adr-skills` リポジトリ）に、既存プロジェクト由来の決定内容・プロジェクト名・ファイルパス・ADR 番号等を一切含めない。含めるのは一般化されたテンプレートと運用ガイドのみ。
- `adr-author` は利用側リポジトリ内でローカル完結する。決定内容を外部サービスやスキルパッケージへ送出しない。実行時の外部 API 呼び出しを行わない。

## テスト方針

- `adr` CLI は TDD で実装する。`1 機能 = 1 テストファイル`（`test_new.py` ← `new`、`test_accept.py` ← `accept`、`test_supersede.py` ← `supersede`、`test_check.py` ← `check`）。実装前にテスト作成 → Red 確認 → 実装（Green）→ リファクタリング。
- スキルは `skill-creator` の eval で description の発火精度を確認する。
- 品質チェック: コミット前に `ruff check --fix . && ruff format . && mypy .`。

## 配布

- APM 配布対応（任意）。`apm install drillan/adr-skills --target claude` 等で `skills/adr-init`・`skills/adr-author` がエージェントのスキルディレクトリに配置される。
- `gh skill install` 形式にも互換（`sphinx-skills` と同じ）。

## スキル構成

2 スキル構成（`adr-init` / `adr-author`）。supersede・status 昇格は `adr-author` + CLI でカバーする。lifecycle 専用スキルは設けない。

## YAGNI（対象外）

- ADR の自動 Accept（人間の決定であり機械化しない）。
- 黙ってのファイル自動生成（合意原則に反する）。
- ADR ライフサイクル専用スキル（薄すぎるため `adr-author` に統合）。
- Claude Code hook / git hook による自動起動（エージェント横断の一貫性と合意原則を優先し、発火はスキル description、安全網は `adr check` とする）。

## 未決事項

なし（設計レビューで全て解決済み）。
```
