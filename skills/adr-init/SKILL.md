---
name: adr-init
description: ADR (Architecture Decision Record) の置き場を Sphinx プロジェクトに用意する。「ADR 管理を始めたい」「ADR を初期化」と依頼された場面で発火する。既存 Sphinx プロジェクトがあればその配下に ADR セクションを追加し、無ければ ADR 専用の Sphinx プロジェクトを新規生成する。
license: MIT
allowed-tools: Bash, Read, Write, Edit, Glob
---

## ステップ 1: モード判定

Glob で対象リポジトリ内の `conf.py` を検索する。

```
**/conf.py
```

- `conf.py` が見つかった場合 → **セクション追加モード**へ進む。
- `conf.py` が見つからない場合 → **スタンドアロンモード**へ進む。

`conf.py` が複数マッチした場合（monorepo 等）は、リポジトリルートに最も近い（パス階層が最も浅い）`conf.py` を既定の `<sphinx-root>` とする。それでも判断がつかない場合（同階層に複数ある等）は、どの Sphinx プロジェクトに ADR セクションを追加するかをユーザーに確認する。

---

## セクション追加モード（既存 Sphinx プロジェクトを検出した場合）

### ステップ 2-A: ADR セクションディレクトリを作成する

検出した `conf.py` が置かれているディレクトリを `<sphinx-root>` とする。
`<sphinx-root>/adr/` ディレクトリと `<sphinx-root>/adr/_templates/` ディレクトリを作成する。

### ステップ 2-B: テンプレートファイルを配置する

このスキルディレクトリ（`skills/adr-init/`）の `templates/` から以下をコピーする。

| コピー元（スキルの templates/） | コピー先 |
|---|---|
| `templates/index.md` | `<sphinx-root>/adr/index.md` |
| `templates/_templates/adr_template.md` | `<sphinx-root>/adr/_templates/adr_template.md` |

`index.md` は glob toctree（`[0-9][0-9][0-9][0-9]-*`）を含んでいるため、ADR ファイル追加後に `index.md` を編集する必要はない。

### ステップ 2-C: 親プロジェクトの index.md に ADR セクションを組み込む

`<sphinx-root>/index.md`（または `index.rst`）の `{toctree}` ブロックに `adr/index` を追加する。

- toctree エントリは**拡張子なし**で記述する（`adr/index` であって `adr/index.md` ではない）。
- 既に `adr/index` が含まれていれば何もしない。
- ファイルが RST 形式の場合は `.. toctree::` ディレクティブに追記する。例:

  ```rst
  .. toctree::

     adr/index
  ```

### ステップ 2-D: conf.py の exclude_patterns を更新する

`<sphinx-root>/conf.py` の `exclude_patterns` に `'adr/_templates'` を追加する。

- 既に含まれていれば何もしない。
- `adr_template.md` が Sphinx のビルド対象に含まれないようにするための設定。

例（既存リストへの追記）:

```python
exclude_patterns = ["_build", "Thumbs.db", ".DS_Store", "adr/_templates"]
```

### ステップ 2-E: myst_parser の確認

`<sphinx-root>/conf.py` の `extensions` に `myst_parser` が含まれていない場合、`sphinx-config` スキルを使って追加することを提案する（強制ではない）。`sphinx-config` スキルが使えない場合は親 `conf.py` の `extensions` を直接編集してもよい。

---

## スタンドアロンモード（既存 Sphinx プロジェクトが無い場合）

### ステップ 3-A: 配置先ディレクトリを決める

既定の配置先は `docs/adr/`。ユーザーが別のパスを指定していればそちらを使う。

### ステップ 3-B: テンプレートツリーをコピーする

このスキルディレクトリの `templates/` ツリー全体を配置先へコピーする。

| コピー元（スキルの templates/） | コピー先 |
|---|---|
| `templates/conf.py` | `<配置先>/conf.py` |
| `templates/index.md` | `<配置先>/index.md` |
| `templates/Makefile` | `<配置先>/Makefile` |
| `templates/make.bat` | `<配置先>/make.bat` |
| `templates/_static/.gitkeep` | `<配置先>/_static/.gitkeep` |
| `templates/_templates/adr_template.md` | `<配置先>/_templates/adr_template.md` |

### ステップ 3-C: conf.py のプレースホルダを置換する

コピーした `<配置先>/conf.py` の以下のプレースホルダを実値で置換する。

| プレースホルダ | 置換値 |
|---|---|
| `{{PROJECT}}` | プロジェクト名（ユーザー指定、または推定できる場合はリポジトリ名） |
| `{{AUTHOR}}` | 著者名（ユーザー指定） |
| `{{YEAR}}` | 現在の年（4 桁） |

プロジェクト名・著者名が不明な場合はユーザーに確認してから置換する。

---

## 共通事項（両モード）

- ADR ファイル本体（`NNNN-<slug>.md`）と `index.md` の構造は両モードで共通。`adr-author` スキルはこの共通構造に対して動作する。
- 完了後、`adr-author` スキルで最初の ADR を起票できる旨をユーザーに案内する。
- Sphinx のビルド・テーマ運用には `sphinx-skills`（drillan/sphinx-skills）が利用可能である旨を案内する（ハード依存ではなく参考案内）。
- ADR が 1 件も無い状態で `sphinx-build -W`（警告をエラー化）を実行すると、`adr/index.md` の glob toctree（`[0-9][0-9][0-9][0-9]-*`）が空マッチ警告を出しビルドが失敗する。これは初期化直後の想定内の挙動であり、`adr-author` で最初の ADR を起票すれば解消する。最初の ADR を起票するまでは `-W` なしでビルドする。
