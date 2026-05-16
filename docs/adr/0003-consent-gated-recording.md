---
adr: "0003"
title: "ADR 記録は合意ゲートを必須とし発火はスキル description で行う"
status: Proposed
date: 2026-05-16
deciders:
  - driller
supersedes: null
superseded_by: null
---

# ADR-0003: ADR 記録は合意ゲートを必須とし発火はスキル description で行う

## Context

- ADR は本来「deciders の合意を記録する」ものであり、ツールが黙ってファイルを自動生成する行為は ADR の本質に反する。
- エージェントがアーキテクチャ上の決定を検知した場合に「どのタイミングで・どのように」ADR 記録をトリガーするかを決める必要があった。
- 候補として、(a) git hook / Claude Code hook で自動起動する案、(b) スキルの description 発火でエージェントが提案しユーザーが合意する案、の 2 つが検討された。
- hook を使う場合、複数のコーディングエージェントで一貫した挙動を保証することが難しく、またユーザーが承認する前にファイルが生成されてしまうリスクがある。

## Decision

ADR ファイルの生成は必ずユーザーの明示的な合意を得た後にのみ行う。発火はスキルの description 設計（アーキテクチャ上の決定が確定した場面で `adr-author` スキルを呼び出す）で実現し、git hook / Claude Code hook による自動起動は採用しない。`check_adr.py` は合意漏れの事後検出の安全網として提供する。

## Consequences

- **良くなること**
  - ADR が常に deciders の合意を経た記録になり、ADR 本来の意味を保持できる。
  - スキル description による発火はエージェント横断で共通の発火条件を定義でき、一貫性が保てる。
  - `check_adr.py` を CI に組み込むことで、合意済みだが記録漏れの ADR を事後検出できる。
- **トレードオフとして受け入れること**
  - スキル description の精度によっては発火漏れが起きる可能性がある（`check_adr.py` で補完する）。
  - ユーザーが合意ステップを踏む必要があるため、完全無人での ADR 生成はできない。

## Alternatives Considered

- **案 A: Claude Code hook / git hook で ADR 記録を自動起動する**
  - 見送り理由: エージェント横断の一貫性を保証できない（hook の実装はエージェント固有）。またユーザーの合意前にファイルが生成される可能性があり、「黙ったファイル自動生成は合意原則に反する」という ADR の本質的要件に違反する。

## 決定時の参考資料（抜粋）

> ✕ 黙ってファイルを自動生成する。
> ○ アーキテクチャ・仕様に関わる決定を**取りこぼさず検知して提案**し、deciders の合意の上で記録する。合意ステップは ADR の本質そのもの。
> エージェント非依存性は 2 箇所で担保する。(1) 機械処理（採番・index 登録・status・supersede）はスクリプトに寄せて完全同一挙動。(2) 取りこぼしは `check_adr.py` で事後検出できる。
> Claude Code hook / git hook による自動起動（エージェント横断の一貫性と合意原則を優先し、発火はスキル description、安全網は `check_adr.py` とする）。

出典: docs/superpowers/specs/2026-05-16-adr-skills-design.md（「『自動記録』の意味（合意済みの定義）」節・「YAGNI（対象外）」節）

## 関連ドキュメント

- spec: docs/superpowers/specs/2026-05-16-adr-skills-design.md
