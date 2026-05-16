---
adr: "0006"
title: "ADR 索引の toctree は glob で自動収集する"
status: Proposed
date: 2026-05-16
deciders:
  - driller
supersedes: null
superseded_by: null
---

# ADR-0006: ADR 索引の toctree は glob で自動収集する

## Context

- `docs/adr/index.md` は ADR の索引ページであり、各 ADR ファイル（`NNNN-slug.md`）を toctree に収録する必要がある。
- `create_adr.py` が ADR ファイルを生成するたびに `index.md` の toctree も更新する方式と、toctree を `:glob:` で自動収集する方式のどちらを採用するかを決める必要があった。
- Sphinx の `:glob:` オプションは `[0-9][0-9][0-9][0-9]-*` のようなパターンでファイルを自動収集できる。スクリプトが `index.md` を直接編集しなくてよくなる。
- なお spec 初稿の `create_adr.py` 仕様行には「`index.md` の toctree と一覧に登録」と記されており、当初はスクリプトが `index.md` を編集する想定だった。計画段階で glob 方式へ変更したため、本 ADR がその個別仕様行を上書きする決定として位置づけられる。

## Decision

`docs/adr/index.md` の toctree に `:glob:` オプションと `[0-9][0-9][0-9][0-9]-*` パターンを使い、ADR ファイルを自動収集する。`create_adr.py` は `index.md` を編集しない。

## Consequences

- **良くなること**
  - `create_adr.py` が `index.md` を編集する必要がなくなり、スクリプトの責務が採番・ファイル生成のみに絞られる。
  - `NNNN-slug.md` を追加するだけで自動的に索引に反映されるため、手動での toctree 管理が不要になる。
  - `index.md` の構造がシンプルに保たれ、壊れにくい。
- **トレードオフとして受け入れること**
  - ADR が 1 件も存在しない場合、glob が空マッチになり Sphinx が警告を出す。初期状態の `index.md` のみの状態では `-W` オプション付きビルドが失敗する（ADR を起票すれば解消）。
  - toctree の表示順は Sphinx の glob 収集順（ファイル名昇順）に依存する。ADR 番号が採番順に振られる前提が必要になる。

## Alternatives Considered

- **案 A: `create_adr.py` が `index.md` の toctree エントリを直接挿入する**
  - 見送り理由: 構造化 Markdown ファイル（toctree ディレクティブを含む）への冪等な文字列挿入は脆弱であり、既存エントリの重複挿入・フォーマット崩壊のリスクがある。スクリプトに Markdown 構造のパース・編集ロジックが入り責務が増える。

## 決定時の参考資料（抜粋）

> `index.md` の toctree に `:glob:` を使い、スクリプトは `index.md` を編集しない。

出典: docs/superpowers/specs/2026-05-16-adr-skills-design.md（タスク記述 ADR-0006「glob-toctree」Decision 要旨）

## 関連ドキュメント

- spec: docs/superpowers/specs/2026-05-16-adr-skills-design.md
