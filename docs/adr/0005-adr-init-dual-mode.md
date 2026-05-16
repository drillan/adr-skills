---
adr: "0005"
title: "adr-init をセクション追加 / スタンドアロンの 2 モードにする"
status: Proposed
date: 2026-05-16
deciders:
  - driller
supersedes: null
superseded_by: null
---

# ADR-0005: adr-init をセクション追加 / スタンドアロンの 2 モードにする

## Context

- `adr-init` スキルは対象リポジトリに ADR の置き場を用意する初期化スキルである。
- 利用者のリポジトリには「既存の Sphinx プロジェクトがある場合」と「Sphinx プロジェクトが存在しない場合」の 2 パターンがある。
- 既存 Sphinx プロジェクトがある場合にスタンドアロンの Sphinx プロジェクトを新規生成すると、2 つの Sphinx プロジェクトが混在し `conf.py` の管理が重複する。一方、既存 Sphinx プロジェクトがない場合にセクション追加のみ対応すると、Sphinx 設定ファイルなしで ADR セクションを使うことになり機能しない。
- いずれのモードでも、ADR ファイル本体（`NNNN-*.md`）と `index.md` の構造は共通にする必要がある（第 1 層スクリプトがこの共通構造に対して動作するため）。

## Decision

`adr-init` スキルを 2 モードで実装する。既存の `conf.py` を検出した場合はその Sphinx プロジェクト配下に ADR セクション（`<sphinx-root>/adr/`）を追加するセクション追加モードを取る。`conf.py` が存在しない場合は ADR 専用の Sphinx プロジェクトを新規生成するスタンドアロンモードを取る。

## Consequences

- **良くなること**
  - 既存 Sphinx プロジェクトを持つリポジトリでは `conf.py` を新設せず親のものを再利用でき、設定の二重管理を避けられる。
  - Sphinx プロジェクトを持たないリポジトリでもすぐに ADR 管理を開始できる。
  - ADR ファイルと `index.md` の構造が共通なため、第 1 層スクリプトはモードを意識せず動作できる。
- **トレードオフとして受け入れること**
  - 2 モードの分岐ロジックを `adr-init` スキル本文で管理する必要があり、SKILL.md が複雑になる。
  - セクション追加モードでは親の `conf.py` に `myst_parser` がない場合の追加提案が必要になり、別スキル（`sphinx-config`）との連携が要る。

## Alternatives Considered

- **案 A: セクション追加モードのみ対応する（既存 Sphinx プロジェクト前提）**
  - 見送り理由: Sphinx プロジェクトを持たないリポジトリで ADR 管理を始めたい利用者をサポートできない。

- **案 B: スタンドアロンモードのみ対応する（常に新規 Sphinx プロジェクトを生成）**
  - 見送り理由: 既存 Sphinx プロジェクトがある場合に `conf.py` が 2 つ存在することになり、ビルド設定が重複・競合する。

## 決定時の参考資料（抜粋）

> 対象リポジトリに ADR の置き場を用意する。既存 Sphinx プロジェクトの有無で 2 モードに分岐する。
> **セクション追加モード**（既存 `conf.py` を検出した場合）: その Sphinx プロジェクト配下に ADR セクション `<sphinx-root>/adr/` を作る。`index.md`（ADR セクションの目次）と `_templates/adr_template.md` を配置し、親プロジェクトの `index.md` の toctree に `adr/index` を 1 度だけ組み込む。`conf.py` は新設せず親のものを再利用する。
> **スタンドアロンモード**（既存 Sphinx プロジェクトが無い場合）: ADR 専用の Sphinx プロジェクトを新規生成する。

出典: docs/superpowers/specs/2026-05-16-adr-skills-design.md（「`adr-init` スキル」節）

## 関連ドキュメント

- spec: docs/superpowers/specs/2026-05-16-adr-skills-design.md
