---
adr: "0004"
title: "第 1 層スクリプトを利用側リポジトリへ vendoring しない"
status: Proposed
date: 2026-05-16
deciders:
  - driller
supersedes: null
superseded_by: null
---

# ADR-0004: 第 1 層スクリプトを利用側リポジトリへ vendoring しない

## Context

- 第 1 層スクリプト（`create_adr.py` 等）はスキル同梱で配布されることが ADR-0002 で決まった。利用者が `adr-skills` をインストールすると、スクリプトはエージェントのスキルディレクトリ（`.claude/skills/adr-author/scripts/`）に配置される。
- スクリプトを利用側リポジトリへコピー（vendoring）する方式も検討された。vendoring すれば外部依存なしでスクリプトを実行できるが、スクリプトのアップデートが利用側リポジトリへ手動で伝搬されない問題が生じる。
- APM の skill bundle は「the entire directory is copied to `<target>/skills/<name>/`, preserving internal structure」であり、スクリプトはスキルバンドル内から `--adr-dir` 引数で対象ディレクトリを受け取って動作できる設計になっている。

## Decision

第 1 層スクリプトを利用側リポジトリへコピー（vendoring）しない。スクリプトはスキルバンドル内（`.claude/skills/adr-author/scripts/`）から呼び出し、対象 ADR ディレクトリは `--adr-dir` 引数で受け取る。

## Consequences

- **良くなること**
  - スクリプトのアップデートは `apm update` でのみ管理され、利用側リポジトリを汚染しない。
  - 利用側リポジトリにスクリプトのコピーが存在しないため、保守コストが二重化しない。
  - スキルバンドルとスクリプトが常に同一バージョンで動作する。
  - 第 1 層スクリプトは標準ライブラリのみで自己完結しているため、vendoring しなくても利用側リポジトリに外部依存（サードパーティパッケージ）を持ち込まない。vendoring の唯一のメリットだった「外部依存なしでの実行」は、自己完結設計によって vendoring なしでも達成されている。
- **トレードオフとして受け入れること**
  - スキルがインストールされていない環境（APM なし・スキルディレクトリが存在しない）では、スクリプトを直接呼び出せない。
  - スクリプトのパスがスキルディレクトリに依存するため、呼び出し元がパスを知っている必要がある。

## Alternatives Considered

- **案 A: スクリプトを利用側リポジトリへ vendoring する**
  - 見送り理由: APM 配布の制約上、スクリプトはスキルバンドル内から動作するため vendoring は不要。vendoring するとアップデートが二重管理になり、バージョン不一致が生じるリスクがある。

## 決定時の参考資料（抜粋）

> APM の skill bundle は「the entire directory is copied to `<target>/skills/<name>/`, preserving internal structure」であり、スキルディレクトリ配下のサブディレクトリ（`scripts/`・`templates/` 等）はスキル本体ごとエージェントのスキルディレクトリ（`.claude/skills/` 等）へ配置される。
> 一方、リポジトリルートの `pyproject.toml` / `uv.lock` / `tests/` は `~/.apm/apm_modules/` にキャッシュされるが配置対象外。したがって**第 1 層のスクリプトは `skills/adr-author/` の中に同梱**し、かつ**標準ライブラリのみで自己完結**させる。利用側リポジトリへスクリプトをコピー（vendoring）する必要はない — スクリプトはスキルバンドル内から、対象 ADR ディレクトリを引数に取って動作する。

出典: docs/superpowers/specs/2026-05-16-adr-skills-design.md（「APM 配布の制約（公式ドキュメント確認済み）」節）

## 関連ドキュメント

- spec: docs/superpowers/specs/2026-05-16-adr-skills-design.md
