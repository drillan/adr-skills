# 利用方法

このページは、`adr-skills` を導入したリポジトリで 2 つのスキルをどう使うかを説明します。想定読者は、Claude Code などのエージェントを使って開発を進める開発者です。スキルの導入（`apm install`）は済んでいる前提とします。導入・更新・削除の手順はリポジトリ README を参照してください。

## スキルが発火する仕組み

`adr-init` と `adr-author` は、エージェントとの会話の文脈に応じて自動で発火します。各スキルの発火条件は `SKILL.md` の description に書かれており、エージェントがその記述と会話内容を照らし合わせて判断します。

自動発火を待たずに、「ADR 管理を始めたい」「ADR を書いて」のように明示的に依頼してもかまいません。

## ADR の置き場を初期化する（adr-init）

最初に `adr-init` で ADR の置き場を用意します。「ADR 管理を始めたい」「ADR を初期化」と依頼すると発火します。

`adr-init` はリポジトリ内の `conf.py` を探し、その有無で動作を変えます。

```{table} adr-init の 2 つのモード
:widths: auto

| モード | 条件 | 動作 |
|---|---|---|
| セクション追加 | 既存の Sphinx プロジェクト（`conf.py`）がある | その配下に `adr/` セクションを追加し、親の `index.md` の toctree に組み込む |
| スタンドアロン | 既存の Sphinx プロジェクトがない | 既定で `docs/adr/` に ADR 専用の Sphinx プロジェクトを新規生成する |
```

どちらのモードでも、次のファイルが置かれます。

- `adr/index.md`: ADR の目次。glob toctree（`[0-9][0-9][0-9][0-9]-*`）を含むため、ADR を追加しても目次を手で編集する必要はありません。
- `adr/_templates/adr_template.md`: ADR ファイルのテンプレート。

スタンドアロンモードでは、これらに加えて `conf.py` や `Makefile` など Sphinx プロジェクトの構成ファイルも生成されます。

## 決定を ADR に記録する（adr-author）

設計上の決定を ADR として記録するのが `adr-author` です。次の場面で発火します。

- design spec（`docs/superpowers/specs/*-design.md`）を書いた直後
- フレームワーク・ライブラリ・境界・プロトコル・データ構造の選定など、代替案を伴う設計判断が確定した場面
- 「ADR を書いて」と明示的に依頼された場面

バグ修正・リファクタリング・ドキュメント更新のように決定を伴わない作業では発火しません。

`adr-author` は次の流れで動きます。

1. spec や会話から、記録すべき決定を抽出します。1 つの設計判断が複数の決定を含むこともあり、その場合は ADR の候補を複数挙げます。
2. 候補ごとに Context・Decision・Consequences・Alternatives の 4 要素を起草します。
3. 起草した内容をプレビューとして提示し、ユーザーの合意を求めます（合意ゲート）。
4. 合意が得られた後にスクリプトを実行し、ADR ファイルを生成します。

合意ゲートでは、次の形式でプレビューが提示されます。

```text
次の決定を ADR-NNNN として記録します。

タイトル: <タイトル>
slug: <slug>
Context: <要約>
Decision: <要約>
Consequences: <要約>
Alternatives: <要約>

ADR 化してよいですか？（yes / no / 修正点があれば指摘）
```

`ADR-NNNN` の番号は提示時点では暫定で、確定番号はファイル生成時に採番されます。生成された ADR の status は `Proposed` です。`adr-author` が自動で `Accepted` にすることはありません。

## ステータスの昇格と supersede

`Proposed` の ADR を `Accepted` に昇格させるのは、人間によるレビューを経た別の判断です。「ADR-0003 を Accepted にして」のように依頼すると、`adr-author` がプレビューを提示し、合意の後に反映します。

決定を変更したいときは、既存の ADR を書き換えず、新しい ADR を起こして古い ADR を置き換えます（supersede）。「ADR-0002 を 0007 で置き換えて」のように依頼すると、古い ADR に `superseded_by`、新しい ADR に `supersedes` が記録されます。古いファイルはそのまま残ります。

昇格と supersede も、ADR の新規作成と同じく「提示 → 合意 → 反映」の順序で進みます。ステータスの考え方は、リポジトリ README の「ADR の運用方針」を参照してください。

## 未初期化のときの挙動

ADR の置き場（`index.md` と `_templates/adr_template.md`）がまだ無い状態で `adr-author` を使おうとした場合、`adr-author` は処理を進めません。`adr-init` の実行を促して作業を止めます。先に `adr-init` で初期化してください。
