---
name: adr-author
description: アーキテクチャ・仕様に関わる決定を ADR (Architecture Decision Record) として記録する。superpowers の design spec (docs/superpowers/specs/*-design.md) が書かれた直後、またはフレームワーク・ライブラリ・境界・プロトコル・データ構造の選定で代替案を伴う決定が確定した場面、または「ADR を書いて」と明示依頼された場面で発火する。バグ修正・リファクタリング・ドキュメント更新など決定を伴わない作業では発火しない。
license: MIT
allowed-tools: Bash, Read, Write, Edit, Glob, Grep
---

## ベストプラクティス

1. **1 ADR = 1 決定。** 決定と理由に集中し、実装詳細（ファイル名・関数シグネチャ等）は書かない。
2. **Accepted 後の ADR は不変。** 変更が必要な場合は新しい ADR を起こして supersede する。
3. **ステータス遷移は一方向。** `Proposed` → `Accepted` → `Deprecated` / `Superseded`。逆方向の遷移は行わない。
4. **代替案・却下理由・トレードオフを正直に記録する。** 採用案だけでなく、検討した選択肢と却下の根拠を必ず書く。
5. **フロントマターは MADR 系フィールドを使う。** `adr` / `title` / `status` / `date` / `deciders` / `supersedes` / `superseded_by` を基本とする。
6. **出典抜粋は ADR 内に貼り付けて凍結する。** 動的 include（外部ファイル参照）は採用しない。spec の該当箇所は ADR 内にコピーして埋め込む。

## ワークフロー

### ステップ 1: 決定を抽出する

spec や会話から記録すべき決定を特定する。1 つの設計判断が複数の独立した決定を含むことは珍しくない。複数 ADR 候補が出ることを許容し、候補をリストアップする。

### ステップ 2: 各候補を起草する

候補ごとに以下の 4 要素を起草する:

- **Context:** なぜこの決定が必要になったか（背景・制約）
- **Decision:** 何を決めたか（主文）
- **Consequences:** この決定がもたらす結果（メリット・デメリット）
- **Alternatives:** 検討したが採用しなかった代替案と却下理由

spec の該当箇所は引用として ADR に貼り付けて凍結する。

### ステップ 3: 【合意ゲート・必須】ユーザーに提示して合意を取る

> **この手順はスキップ不可。合意なしに次ステップへ進んではならない。**

ユーザーに以下の形式でプレビューを提示する:

```
次の決定を ADR-NNNN として記録します。

タイトル: <タイトル>
slug: <slug>
Context: <要約>
Decision: <要約>
Consequences: <要約>
Alternatives: <要約>

ADR 化してよいですか？（yes / no / 修正点があれば指摘）
```

プレビューの「ADR-NNNN」の NNNN は暫定番号（現時点の最大番号 +1 の見込み）であり、確定番号は `create_adr.py` 実行時に採番される。

ADR 化の要否・内容の修正・番号の確認を含めて合意を取る。ユーザーから明示的な承認が得られるまで次へ進まない。

### ステップ 4: 合意後にスクリプトを実行してファイルを生成する

合意が得られたら `create_adr.py` を実行する。status は常に `Proposed` で作成される（スキルが自動で Accepted にしない）。

### ステップ 5: supersede・status 変更も同手順で行う

supersede や Accepted 昇格を行う場合も「提示 → 合意 → スクリプト実行」の順序を守る。**Accepted への昇格は人間の別判断であり、スキルが自動で行わない。**

なお、`Superseded` への遷移は `set_status.py` ではなく `supersede.py` を使う（`set_status.py` は `Superseded` 指定を拒否する）。

## スクリプトの呼び出し方

スクリプトはこの SKILL.md と同じスキルディレクトリ内の `scripts/` にある。

実行はカレントディレクトリに依存しない。`python <このスキルのディレクトリ>/scripts/create_adr.py ...` のように、スキルディレクトリを起点としたパスで呼べばよい（環境に `uv` があれば `uv run python <このスキルのディレクトリ>/scripts/create_adr.py ...`）。`cd` や `PYTHONPATH` の設定は不要。

対象 ADR がどこにあるかは CWD ではなく `--adr-dir` 引数で指定する。

以下の例ではスキルディレクトリにいる前提で `scripts/...` と表記するが、実際にはスキルディレクトリへの絶対パスまたは相対パスを前置してよい。

### 新規作成

```bash
python scripts/create_adr.py \
  --adr-dir <ADRディレクトリ> \
  --title <タイトル> \
  --slug <英小文字-ハイフンのslug> \
  --decider <名前> [--decider <名前2> ...] \
  [--spec <specパス>] \
  [--date <YYYY-MM-DD>]
```

- `--title`: 日本語可
- `--slug`: `[a-z0-9-]+` のみ（英小文字・数字・ハイフン）
- `--decider`: 1 つ以上必須、複数指定可
- `--spec`: 参照 spec のパス（省略可）
- `--date`: 省略時は今日の日付
- 採番・テンプレ展開・ファイル生成のみ行う。`index.md` は glob toctree のため編集不要。

### status 遷移（Accepted / Deprecated）

```bash
python scripts/set_status.py \
  --adr-dir <ADRディレクトリ> \
  --number <NNNN> \
  --status <Accepted|Deprecated>
```

### supersede

```bash
python scripts/supersede.py \
  --adr-dir <ADRディレクトリ> \
  --number <旧NNNN> \
  --by <新MMMM>
```

### 点検（spec と ADR の対応確認）

```bash
python scripts/check_adr.py \
  --adr-dir <ADRディレクトリ> \
  --specs-dir <specディレクトリ>
```

## 未初期化の扱い

ADR ディレクトリ（`index.md` と `_templates/adr_template.md`）が存在しない場合、暗黙に処理を進めない。ユーザーに `adr-init` スキルの実行を促して作業を停止する。

## 機密保持

他者プロジェクトの決定内容・プロジェクト名・パスをスキルパッケージや外部へ出力しない。ADR は対象リポジトリ内でローカルに完結させる。
