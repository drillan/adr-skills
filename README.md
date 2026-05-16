# adr-skills

ADR (Architecture Decision Record) を合意ベースで起草・管理するスキルパッケージです。

設計上の決定を検知し、ユーザーと合意を取ってから ADR ファイルに記録するまでのフローをカバーします。採番・ステータス遷移・上書き関係 (supersede)・整合性点検は決定的なスクリプト群が担い、判断・起草・合意取得はスキルが担う 2 層設計になっています。

## 提供スキル

| スキル名 | 用途 |
|---|---|
| `adr-init` | ADR 用 Sphinx プロジェクト（スタンドアロン）またはセクション（既存 Sphinx への追加）を初期化する |
| `adr-author` | 決定の検知・起草・合意取得・記録、ステータス変更、supersede を担う |

## アーキテクチャ

### 第 1 層: 決定的スクリプト群

`skills/adr-author/scripts/` にあるスクリプト群です。ファイル操作・採番・ステータス遷移をべき等かつ引数完結で実行します。スキルがこれらを呼び出します。

| スクリプト | 役割 |
|---|---|
| `create_adr.py` | 採番・テンプレート展開・ADR ファイル生成 |
| `set_status.py` | ステータス遷移（`Proposed→Accepted` / `Proposed→Deprecated` / `Accepted→Deprecated`）。`Superseded` は扱わない |
| `supersede.py` | 旧 ADR を `Superseded` にして `superseded_by` を、新 ADR に `supersedes` を記録 |
| `check_adr.py` | spec ファイルに対応する ADR が存在するかを点検 |

共有ライブラリ `adrlib.py` が採番・フロントマター解析／書き込みを提供し、上記スクリプトはこれを利用します。

### 第 2 層: スキル

`adr-author` が決定の抽出・起草・プレビュー提示・合意取得を担います。第 1 層スクリプトを実行するのは合意が得られた後だけです。合意のないままファイルを生成・変更することはありません。

## 導入・更新・削除

[APM](https://github.com/drillan/apm) でスキルを導入・更新・削除します。いずれも APM CLI が必要です（未導入の場合は `curl -sSL https://aka.ms/apm-unix | sh`）。

### インストール

```bash
apm install drillan/adr-skills --target claude
```

`--target` は配置先のエージェントです（`claude` / `copilot` / `codex` / `cursor` / `gemini` など、カンマ区切りで複数指定できます）。複数のプロジェクトで使い回す場合は `-g`（ユーザースコープ）を付けます。

本番運用や CI では、意図しない更新を防ぐためにバージョンを固定します。リリース tag または commit SHA を `#` の後に指定します。

```bash
apm install drillan/adr-skills#<tag> --target claude
```

### 更新

更新できるかを確認してから更新します。

```bash
apm outdated   # 更新可能なパッケージを一覧表示
apm update     # apm.lock.yaml を再生成し、スキルを最新版で再配置
```

バージョンを固定した依存は `apm update` の対象外です。バージョンを上げるときは `apm.yml` の固定表記を書き換えてから `apm install` し直します。更新後は `apm audit --ci` でセキュリティ検証を行えます。

### アンインストール

削除は破壊的な操作です。`--dry-run` で対象を確認してから実行します。

```bash
apm uninstall drillan/adr-skills --dry-run   # 削除されるファイルを事前表示
apm uninstall drillan/adr-skills             # apm.yml・apm.lock.yaml と配置済みファイルを同期削除
```

ユーザースコープに導入したものは、`-g` を付けて削除します。

## 利用方法

2 つのスキルは、エージェント（Claude Code など）との会話の文脈に応じて自動で発火します。「ADR を書いて」のように明示的に依頼しても発火します。

1. ADR の置き場を初期化します。「ADR 管理を始めたい」と依頼すると `adr-init` が発火し、Sphinx プロジェクトの配下に ADR セクションを用意します。
2. 決定を ADR に記録します。design spec を書いた直後や、代替案を伴う設計判断が確定した場面で `adr-author` が発火します。「ADR を書いて」と明示依頼してもかまいません。
3. 提示された ADR 案に合意します。`adr-author` は ADR 案をプレビューとして提示し、承認を求めます。承認の後にだけファイルが生成されます。
4. ステータスを進めたり、別の ADR で置き換えたりします。「ADR-0003 を Accepted にして」のように依頼すると、同じく提示と合意を経て反映されます。

各スキルの発火条件・モード・ワークフローの詳細は [docs/usage.md](docs/usage.md) を参照してください。

本パッケージ自身の設計決定も、これらのスキルで [docs/adr/](docs/adr/) に記録しています。実際の ADR の書き方の例として参照できます。

## ADR の運用方針

本パッケージは次の運用を前提に設計しています。スクリプトとスキルの挙動もこの方針に沿います。

- 1 つの ADR には 1 つの決定だけを記録します。独立した決定が複数あるときは ADR を分けます。
- Accepted になった ADR はそのまま残し、内容は書き換えません。方針を変えるときは新しい ADR を起こして supersede します。
- 採用した案だけでなく、検討して見送った案とその理由、トレードオフも記録します。
- ステータスは前進方向にのみ動かします。`set_status.py` が許可する遷移は `Proposed → Accepted`、`Proposed → Deprecated`、`Accepted → Deprecated` です。`Superseded` は別の ADR で置き換えるときに `supersede` 操作で付与します。
