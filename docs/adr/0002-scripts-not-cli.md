---
adr: "0002"
title: "第 1 層を CLI でなくスキル同梱スクリプトで実装する"
status: Proposed
date: 2026-05-16
deciders:
  - driller
supersedes: null
superseded_by: null
---

# ADR-0002: 第 1 層を CLI でなくスキル同梱スクリプトで実装する

## Context

- ADR-0001 で第 1 層（決定的処理）をスキルとは別のアーティファクトとして分離することを決めた。その実装形式として「単一エントリポイントを持つ `adr` CLI」と「目的別の小スクリプト群」のどちらを選ぶかを決める必要があった。
- adr-skills の利用者はエージェント（スキル）か、Makefile/CI から呼ぶ開発者である。`pip install` や PATH 設定を必要とする CLI は APM 配布の制約（pyproject.toml はキャッシュされるが配置対象外）と相性が悪い。
- APM の skill bundle は `skills/<name>/` 配下がそのまま `.claude/skills/<name>/` へ配置されるため、スクリプトを `skills/adr-author/scripts/` に置けばインストール後も直接利用できる。

## Decision

`adr create` / `adr set-status` のような単一 CLI を作らず、`create_adr.py` / `set_status.py` / `supersede.py` / `check_adr.py` という目的別の小スクリプト群をスキルに同梱し、スキルが Bash 経由で直接呼び出す形で第 1 層を実装する。

## Consequences

- **良くなること**
  - APM 配布後、追加インストール不要でスクリプトをそのまま利用できる。
  - 各スクリプトが単一責任を持ち、テストが書きやすく、独立して呼び出せる。
  - スクリプト単体を人間が直接 `python scripts/create_adr.py` で呼び出せる。
  - CLI のサブコマンドパーサーやバージョン管理が不要で実装が簡素になる。
- **トレードオフとして受け入れること**
  - スクリプトへの入り口が複数になるため、スキル SKILL.md に呼び出し例を明記する必要がある。
  - `python scripts/xxx.py` という呼び出し形式は単一 CLI と比べてやや冗長に見える。

## Alternatives Considered

- **案 A: `adr` CLI（サブコマンド形式）を作る**
  - 見送り理由: 人間向けのコマンド体験や CLI 単体での CI 実行は要件になく過剰。APM 配布では `pyproject.toml` が配置対象外のため `pip install` した CLI を前提にできない。エントリポイント管理・バージョニングのコストが生じる。

## 決定時の参考資料（抜粋）

> `adr` CLI（単一エントリ + サブコマンド）。決定的処理はスキル同梱スクリプトで足り、人間向けコマンド体験やスキル非導入での CI 実行は要件にないため設けない。

出典: docs/superpowers/specs/2026-05-16-adr-skills-design.md（「YAGNI（対象外）」節）

## 関連ドキュメント

- spec: docs/superpowers/specs/2026-05-16-adr-skills-design.md
