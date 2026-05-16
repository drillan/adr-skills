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
- フロントマターは MADR 系（`adr` / `title` / `status` / `date` / `deciders` / `supersedes` / `superseded_by`）。
- 出典抜粋は ADR 内に貼り付けて凍結する（動的 include は採用しない）。

## アーキテクチャ：2 層モデル

「自動記録」を 1 つの機構で実現しようとするとエージェント依存になる。責務を 2 層に分離する。

### 第 1 層：決定的な機構（エージェント非依存）— スキル同梱スクリプト

純粋な機械的処理のみを担う。文章は書かない。冪等。エラー時はデフォルト値で続行せず例外を送出する。Python 製で、**標準ライブラリのみで自己完結**する（APM は `pyproject.toml` を配置しないため、外部依存に頼れない）。`adr-author` スキルに同梱し、スキルが Bash 経由で呼び出す。対象リポジトリの ADR ディレクトリは引数で受け取る。

| スクリプト | 役割 |
|---|---|
| `scripts/create_adr.py` | 次番号を採番し `_templates/adr_template.md` を展開して `NNNN-slug.md` を生成。`index.md` の toctree と一覧に登録。`status: Proposed`。 |
| `scripts/set_status.py` | フロントマターの `status` を遷移させ（例: `Proposed` → `Accepted`、→ `Deprecated`）、`index.md` 一覧の該当節を移動。 |
| `scripts/supersede.py` | 旧 ADR に `superseded_by`、新 ADR に `supersedes` を相互リンクし、ステータスを更新。旧ファイルは残す（不変性）。 |
| `scripts/check_adr.py` | spec に対応する ADR が無いものを列挙する。**生成はしない**（合意原則）。終了コードで未記録の有無を返す。 |

どのコーディングエージェント（claude / codex / copilot 等）で作業しても、スクリプトの挙動は完全に同一になる。人間が直接実行することもできる（`python scripts/check_adr.py <adr-dir>` 等）。

### 第 2 層：起草（人間またはエージェント）— `adr-author` スキル

決定の抽出、ADR 化の要否判断、Context / Decision / Consequences / Alternatives の起草、ユーザーへの提案と合意取得を担う。本質的に推論が要るためエージェントまたは人間の仕事。エージェント差は「呼びかけの精度」と「文章の質」に限定され、第 1 層の正しさには影響しない。

## 成果物の構成

```
adr-skills/
├── apm.yml                       # APM 配布メタデータ（package_type: skill_bundle）
├── pyproject.toml                # 開発時のみ（ruff / mypy / pytest）。配布対象外
├── uv.lock
├── README.md
├── LICENSE
├── skills/
│   ├── adr-init/
│   │   ├── SKILL.md
│   │   └── templates/            # conf.py / index.md / adr_template.md / Makefile / make.bat / _static/
│   └── adr-author/
│       ├── SKILL.md
│       └── scripts/              # create_adr.py / set_status.py / supersede.py / check_adr.py
├── docs/                         # adr-skills 自身の doc サイト + ADR（ドッグフーディング）
│   ├── conf.py
│   ├── index.md
│   └── adr/                      # adr-skills 自身の ADR セクション
│       ├── index.md
│       ├── _templates/adr_template.md
│       └── NNNN-*.md
├── tests/                        # スクリプトの TDD テスト（配布対象外・CI で実行）
└── .github/workflows/            # lint / test / skill 検証
```

### APM 配布の制約（公式ドキュメント確認済み）

APM の skill bundle は「the entire directory is copied to `<target>/skills/<name>/`, preserving internal structure」であり、スキルディレクトリ配下のサブディレクトリ（`scripts/`・`templates/` 等）はスキル本体ごとエージェントのスキルディレクトリ（`.claude/skills/` 等）へ配置される。

一方、リポジトリルートの `pyproject.toml` / `uv.lock` / `tests/` は `~/.apm/apm_modules/` にキャッシュされるが配置対象外。したがって **第 1 層のスクリプトは `skills/adr-author/` の中に同梱**し、かつ**標準ライブラリのみで自己完結**させる。利用側リポジトリへスクリプトをコピー（vendoring）する必要はない — スクリプトはスキルバンドル内から、対象 ADR ディレクトリを引数に取って動作する。

## コンポーネント詳細

### 第 1 層スクリプト（`skills/adr-author/scripts/`）

- 状態とロジックを分離する。フロントマター・`index.md` の読み書きをコントラクトとして厳密に扱う。
- `index.md` への登録は冪等（既に登録済みなら何もしない）。
- 採番は既存 `NNNN-*.md` を走査して最大値 +1。4 桁ゼロ埋め。
- 不正な状態遷移（例: 存在しない ADR の status 遷移、Accepted を再 accept）は例外送出。
- フロントマターは固定スキーマ。標準ライブラリのみで読み書きし、外部 YAML ライブラリに依存しない。

### `adr-init` スキル

対象リポジトリに ADR の置き場を用意する。既存 Sphinx プロジェクトの有無で 2 モードに分岐する。

- **セクション追加モード**（既存 `conf.py` を検出した場合）: その Sphinx プロジェクト配下に ADR セクション `<sphinx-root>/adr/` を作る。`index.md`（ADR セクションの目次）と `_templates/adr_template.md` を配置し、親プロジェクトの `index.md` の toctree に `adr/index` を 1 度だけ組み込む。`conf.py` は新設せず親のものを再利用する。親 `conf.py` に `myst_parser` が無ければ `sphinx-config` スキルでの追加を提案する。
- **スタンドアロンモード**（既存 Sphinx プロジェクトが無い場合）: ADR 専用の Sphinx プロジェクトを新規生成する。配置先の既定は `docs/adr/`（ユーザー指定で上書き可）。`templates/` から `conf.py` / `index.md` / `_templates/adr_template.md` / `Makefile` / `make.bat` / `_static/` を配置し、プロジェクト名等のメタデータを埋める。ADR 用 Sphinx の標準構成（`myst_parser` + `sphinx_oceanid` + `shibuya` テーマ + 日本語 LaTeX）。
- いずれのモードでも、ADR ファイル本体（`NNNN-*.md`）と `index.md` の構造は共通。第 1 層スクリプトはこの共通構造に対して動作する。
- Sphinx のビルド・テーマ運用は `sphinx-skills` をソフト参照（README で案内、ハード依存にしない）。
- 発火条件（description）: 「ADR 管理を始めたい」「ADR を初期化」等。

### `adr-author` スキル

中核。仕様・アーキテクチャに関わる決定が生じた場面で発火し、合意の上で ADR を記録する。`scripts/` を同梱し、機械的処理はスクリプトに委譲する。

**発火条件（description 設計）**

- 発火する: superpowers の spec (`docs/superpowers/specs/*-design.md`) が書かれた直後 / アーキテクチャに関わる選択（フレームワーク・ライブラリ・境界・プロトコル・データ構造の選定で**代替案を伴う**もの）が確定した場面 / 明示依頼「ADR を書いて」。
- 発火しない（除外）: バグ修正・リファクタリング・ドキュメント更新・UI 微調整など決定を伴わない作業。

**ワークフロー**

1. 決定を抽出する。1 つの spec から複数 ADR 候補が出ることを許容する（1 つの設計判断が複数の独立した決定を含むことは珍しくないため）。
2. 各候補について Context / Decision / Consequences / Alternatives を起草し、spec の該当箇所を抜粋して凍結する。
3. **ユーザーに提示する**:「次の決定を ADR-NNNN としてこう記録します」とプレビューを示し、ADR 化の要否も含めて合意を取る。
4. 合意後、`scripts/create_adr.py` を呼んでファイルを実体化する（`status: Proposed`）。
5. supersede・Accepted 昇格も同手順（提示 → 合意 → `scripts/supersede.py` / `scripts/set_status.py`）。`Accepted` への昇格は人間の別判断であり、スキルが自動で行わない。

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
  └─ scripts/create_adr.py を実行  ──▶ 第 1 層スクリプト
                                       ├─ NNNN-slug.md 生成（status: Proposed）
                                       └─ index.md の toctree / 一覧に登録
       │
       ▼
ユーザーレビュー → 合意 → scripts/set_status.py で Accepted へ（別判断・別操作）
```

`scripts/check_adr.py` は spec と ADR の対応を点検し、未記録を**列挙のみ**する（黙って生成しない）。記録漏れ確認を頼まれたときの安全網。

## 「自動記録」の意味（合意済みの定義）

- ✕ 黙ってファイルを自動生成する。
- ○ アーキテクチャ・仕様に関わる決定を**取りこぼさず検知して提案**し、deciders の合意の上で記録する。合意ステップは ADR の本質そのもの。
- エージェント非依存性は 2 箇所で担保する。(1) 機械処理（採番・index 登録・status・supersede）はスクリプトに寄せて完全同一挙動。(2) 取りこぼしは `check_adr.py` で事後検出できる。

## エラー処理方針

- フォールバック禁止。スクリプトはエラー時にデフォルト値で続行せず例外を送出する。
- `adr-author` は ADR プロジェクト未初期化（`index.md` や `_templates/` が無い）を検知したら、暗黙に進めず「先に `adr-init` を実行してください」と明示する。
- 不正な状態遷移はスクリプトが拒否し、理由を明示する。

## 機密保持（不変条件）

- スキルパッケージ（`adr-skills` リポジトリ）に、既存プロジェクト由来の決定内容・プロジェクト名・ファイルパス・ADR 番号等を一切含めない。含めるのは一般化されたテンプレートと運用ガイドのみ。
- `adr-author` は利用側リポジトリ内でローカル完結する。決定内容を外部サービスやスキルパッケージへ送出しない。実行時の外部 API 呼び出しを行わない。

## テスト方針

- 第 1 層スクリプトは TDD で実装する。`1 機能 = 1 テストファイル`（`test_create_adr.py` ← `create_adr.py`、`test_set_status.py` ← `set_status.py`、`test_supersede.py` ← `supersede.py`、`test_check_adr.py` ← `check_adr.py`）。実装前にテスト作成 → Red 確認 → 実装（Green）→ リファクタリング。
- スキルは `skill-creator` の eval で description の発火精度を確認する。
- 品質チェック: コミット前に `ruff check --fix . && ruff format . && mypy .`。

## 配布

- APM 配布対応（任意）。`apm install drillan/adr-skills --target claude` 等で `skills/adr-init`・`skills/adr-author`（同梱の `templates/`・`scripts/` ごと）がエージェントのスキルディレクトリに配置される。
- `gh skill install` 形式にも互換（`sphinx-skills` と同じ）。

## スキル構成

2 スキル構成（`adr-init` / `adr-author`）。supersede・status 昇格は `adr-author` + 同梱スクリプトでカバーする。lifecycle 専用スキルは設けない。

## 開発方針：ドッグフーディング

adr-skills 自身のアーキテクチャ決定を、本パッケージが推奨する ADR 規約で `docs/adr/`（既存 `docs/` Sphinx プロジェクト内のセクション）に記録しながら開発する。本ブレストで確定した決定（2 層モデル、`adr` CLI 不採用、hook 不採用、vendoring 不採用、ADR 配置のセクション追加モード 等）が最初の ADR 群になる。

- テンプレート・規約・スクリプトを「自分のリポジトリで通用するか」で継続的に検証でき、利用者への実例にもなる。
- ブートストラップ: `scripts/create_adr.py` が未完成の段階では、最初の ADR はテンプレートから手動で起こす。これがテンプレートの最初のテストになる。スクリプト完成後は以降の ADR 起票・status 操作をスクリプトで行う。
- ここに記録するのは adr-skills 自身の決定であり機密ではない。機密保持の不変条件は他者プロジェクトの決定内容に対するものであり、自プロジェクトの決定記録とは区別する。

## YAGNI（対象外）

- ADR の自動 Accept（人間の決定であり機械化しない）。
- 黙ってのファイル自動生成（合意原則に反する）。
- ADR ライフサイクル専用スキル（薄すぎるため `adr-author` に統合）。
- `adr` CLI（単一エントリ + サブコマンド）。決定的処理はスキル同梱スクリプトで足り、人間向けコマンド体験やスキル非導入での CI 実行は要件にないため設けない。
- 第 1 層スクリプトの利用側リポジトリへの vendoring（スクリプトはスキルバンドル内から動作するため不要）。
- Claude Code hook / git hook による自動起動（エージェント横断の一貫性と合意原則を優先し、発火はスキル description、安全網は `check_adr.py` とする）。

## 未決事項

なし（設計レビューで全て解決済み）。
```
