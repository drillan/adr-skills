# adr-skills

ADR (Architecture Decision Record) を合意ベースで起草・管理するスキルパッケージです。

設計上の決定を検知し、ユーザーと合意を取ってから ADR ファイルに記録するまでのフローをカバーします。採番・ステータス遷移・上書き関係 (supersede)・整合性点検は決定的なスクリプト群が担い、判断・起草・合意取得はスキルが担う 2 層設計になっています。

## 提供スキル

| スキル名 | 用途 |
|---|---|
| `adr-init` | ADR 用 Sphinx プロジェクト（スタンドアロン）またはセクション（既存 Sphinx への追加）を初期化する |
| `adr-author` | 決定の検知・起草・合意取得・記録、ステータス変更、supersede を担う |

## アーキテクチャ

**第 1 層 — 決定的スクリプト群** (`skills/adr-author/scripts/`)

ファイル操作・採番・ステータス遷移をべき等かつ引数完結で実行します。スキルがこれらを呼び出します。

| スクリプト | 役割 |
|---|---|
| `create_adr.py` | 採番・テンプレート展開・ADR ファイル生成 |
| `set_status.py` | ステータス遷移（`Proposed→Accepted` / `Proposed→Deprecated` / `Accepted→Deprecated`）。`Superseded` は扱わない |
| `supersede.py` | 旧 ADR を `Superseded` にして `superseded_by` を、新 ADR に `supersedes` を記録 |
| `check_adr.py` | spec ファイルに対応する ADR が存在するかを点検 |

共有ライブラリ `adrlib.py` が採番・フロントマター解析／書き込みを提供し、上記スクリプトはこれを利用します。

**第 2 層 — スキル**

`adr-author` が決定の抽出・起草・ユーザーへのプレビュー提示・合意取得を担います。合意が得られた後にのみ第 1 層スクリプトを実行します。**合意なしにファイルを生成・変更しない**ことがこのスキルの核心です。

## インストール

[APM](https://github.com/drillan/apm) を使って導入します。

```bash
apm install drillan/adr-skills --target claude
```

## ADR のベストプラクティス

- **1 ADR = 1 決定。** 複数の独立した決定は別々の ADR に分ける。
- **Accepted 後の ADR は不変。** 変更が必要になったら新しい ADR を起こして supersede する。
- **代替案とトレードオフを正直に記録する。** 採用案だけでなく、検討した選択肢と却下の根拠も必ず書く。
- **ステータス遷移は前進のみ。** `Proposed → Accepted`、`Proposed → Deprecated`、`Accepted → Deprecated` のみ許可される。`Superseded` は別 ADR で置き換える際に `supersede` 操作で付与する。逆方向の遷移は行わない。
