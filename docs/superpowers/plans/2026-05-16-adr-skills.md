# adr-skills Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** ADR (Architecture Decision Record) を合意ベースで起草・管理するスキルパッケージ `adr-skills` を構築し、自身の決定をドッグフーディングで記録する。

**Architecture:** 2 層モデル。第 1 層は Python 標準ライブラリのみで自己完結する決定的スクリプト群（`skills/adr-author/scripts/`）。第 2 層は判断・起草・合意取得を担う 2 つのスキル（`adr-init` / `adr-author`）。APM の skill bundle として配布する。

**Tech Stack:** Python 3.13（標準ライブラリのみ、配布スクリプト）、pytest / ruff / mypy（開発時）、Sphinx + MyST（ADR 文書）、APM（配布）。

**計画段階の実装判断（スペックからの精緻化）:** ADR 索引 `index.md` の `{toctree}` は `:glob:` オプションで `NNNN-*.md` を自動収集する。これによりスクリプトは `index.md` を一切編集せず、ADR ファイルのフロントマター操作のみを行う。スペックの「toctree への登録」は glob により自動達成される。

---

## File Structure

| パス | 責務 |
|---|---|
| `apm.yml` | APM 配布メタデータ |
| `pyproject.toml` | 開発時ツール設定（ruff / mypy / pytest）。配布対象外 |
| `LICENSE` / `.gitignore` / `README.md` | パッケージ付帯ファイル |
| `skills/adr-init/SKILL.md` | adr-init スキル本文 |
| `skills/adr-init/templates/` | スタンドアロン ADR Sphinx プロジェクトのテンプレート一式 |
| `skills/adr-author/SKILL.md` | adr-author スキル本文 |
| `skills/adr-author/scripts/adrlib.py` | フロントマター・採番の共有ロジック |
| `skills/adr-author/scripts/create_adr.py` | ADR ファイル生成 |
| `skills/adr-author/scripts/set_status.py` | status 遷移 |
| `skills/adr-author/scripts/supersede.py` | supersede 相互リンク |
| `skills/adr-author/scripts/check_adr.py` | spec と ADR の対応点検 |
| `tests/` | 第 1 層スクリプトの pytest テスト |
| `.github/workflows/ci.yml` | lint / type / test |
| `docs/adr/` | ドッグフーディング: adr-skills 自身の ADR セクション |

スクリプトはすべて `adrlib.py` を共有し、各スクリプトは薄い argparse エントリポイント + 1 つの処理関数で構成する（DRY）。

---

## Task 1: パッケージ骨格と開発ツール設定

**Files:**
- Create: `pyproject.toml`
- Create: `.gitignore`
- Create: `LICENSE`
- Create: `apm.yml`
- Create: `README.md`

- [ ] **Step 1: `.gitignore` を作成**

```
__pycache__/
*.pyc
.pytest_cache/
.ruff_cache/
.mypy_cache/
.venv/
docs/_build/
```

- [ ] **Step 2: `pyproject.toml` を作成**

```toml
[project]
name = "adr-skills"
version = "0.1.0"
description = "ADR を合意ベースで起草・管理するスキルパッケージ"
requires-python = ">=3.13"

[dependency-groups]
dev = ["pytest>=8", "ruff>=0.6", "mypy>=1.11"]

[tool.pytest.ini_options]
pythonpath = ["skills/adr-author/scripts"]
testpaths = ["tests"]

[tool.ruff]
target-version = "py313"

[tool.mypy]
python_version = "3.13"
strict = true
files = ["skills/adr-author/scripts", "tests"]
```

`pythonpath` 設定により、テストは `skills/adr-author/scripts/` のモジュールを直接 import できる。

- [ ] **Step 3: `LICENSE` を作成（MIT、`sphinx-skills` に合わせる）**

MIT ライセンス本文を記載。著作権者は `driller`、年は `2026`。

- [ ] **Step 4: `apm.yml` を作成**

```yaml
name: adr-skills
version: 0.1.0
description: ADR (Architecture Decision Record) を合意ベースで起草・管理するスキル集 (2 個)。ADR プロジェクトの初期化と、決定の検知・提案・記録をカバーする。
```

- [ ] **Step 5: `README.md` を骨格のみ作成**

タイトル `# adr-skills`、1 段落の概要、`## 提供スキル` の表（`adr-init` / `adr-author`）のみ。詳細は Task 12 で補完する。

- [ ] **Step 6: コミット**

```bash
git add pyproject.toml .gitignore LICENSE apm.yml README.md
git commit -m "chore: scaffold adr-skills package metadata"
```

---

## Task 2: ADR テンプレートと adr-init スタンドアロンテンプレート

**Files:**
- Create: `skills/adr-init/templates/adr_template.md`
- Create: `skills/adr-init/templates/index.md`
- Create: `skills/adr-init/templates/conf.py`
- Create: `skills/adr-init/templates/Makefile`
- Create: `skills/adr-init/templates/make.bat`
- Create: `skills/adr-init/templates/_static/.gitkeep`

- [ ] **Step 1: `adr_template.md`（ADR スケルトン）を作成**

第 1 層スクリプトが読み込む雛形。プレースホルダは `{{ }}` 形式。

```markdown
---
adr: "{{ADR}}"
title: "{{TITLE}}"
status: Proposed
date: {{DATE}}
deciders:
{{DECIDERS}}
supersedes: null
superseded_by: null
---

# ADR-{{ADR}}: {{TITLE}}

## Context

何を決める必要があるか。前提と制約を箇条書きで。

## Decision

採用する案を 1〜3 行で明言する。

## Consequences

- **良くなること**
  - ...
- **トレードオフとして受け入れること**
  - ...

## Alternatives Considered

- **案 A: ○○**
  - 見送り理由: ...

## 決定時の参考資料（抜粋）

> 決定時点のスナップショット。出典側は更新されうるが、ここに貼られた内容は凍結される。

## 関連ドキュメント

- spec: {{SPEC}}
```

`{{DECIDERS}}` は `  - name` 行の集合に、`{{SPEC}}` は spec パスまたは `なし` に置換される。

- [ ] **Step 2: `index.md`（ADR 索引、glob toctree）を作成**

```markdown
# Architecture Decision Records (ADR)

アーキテクチャレベルの意思決定を記録する。1 ADR = 1 決定。

## Status 凡例

- **Proposed**: 提案中・レビュー待ち
- **Accepted**: 採用決定
- **Superseded**: 別 ADR に置き換えられた（ファイルは残す）
- **Deprecated**: 破棄されたが歴史的記録として残す

```{toctree}
:maxdepth: 1
:glob:

[0-9][0-9][0-9][0-9]-*
```
```

`:glob:` により `NNNN-*.md` が自動的に索引へ追加される。スクリプトはこのファイルを編集しない。

- [ ] **Step 3: `conf.py`（スタンドアロン ADR プロジェクト用）を作成**

`project` / `author` はプレースホルダ `{{PROJECT}}` / `{{AUTHOR}}`。`extensions = ["myst_parser", "sphinx_oceanid"]`、`myst_enable_extensions = ["colon_fence", "deflist"]`、`language = "ja"`、`html_theme = "shibuya"`、`html_theme_options = {"color_mode": "light"}`、`exclude_patterns = ["_build", "_templates", "Thumbs.db", ".DS_Store"]`。`_templates` を除外することで ADR スケルトンがビルド対象にならない。

- [ ] **Step 4: `Makefile` と `make.bat` を作成**

標準の Sphinx `Makefile` / `make.bat`（`sphinx-quickstart` 生成物と同等）。`SOURCEDIR = .`、`BUILDDIR = _build`。

- [ ] **Step 5: `_static/.gitkeep` を作成（空ディレクトリ保持）**

- [ ] **Step 6: コミット**

```bash
git add skills/adr-init/templates
git commit -m "feat: add adr-init project templates"
```

---

## Task 3: `adrlib.py` — フロントマター共有ロジック（TDD）

**Files:**
- Create: `tests/test_adrlib.py`
- Create: `skills/adr-author/scripts/adrlib.py`

- [ ] **Step 1: 失敗するテストを書く（フロントマター parse/dump）**

`tests/test_adrlib.py`:

```python
from adrlib import AdrError, Frontmatter, dump_frontmatter, next_number, parse_frontmatter

SAMPLE = (
    '---\n'
    'adr: "0001"\n'
    'title: "テスト決定"\n'
    'status: Proposed\n'
    'date: 2026-05-16\n'
    'deciders:\n'
    '  - driller\n'
    'supersedes: null\n'
    'superseded_by: null\n'
    '---\n'
    '\n'
    '# ADR-0001: テスト決定\n'
)


def test_parse_frontmatter_reads_all_fields():
    fm, body = parse_frontmatter(SAMPLE)
    assert fm.adr == "0001"
    assert fm.title == "テスト決定"
    assert fm.status == "Proposed"
    assert fm.date == "2026-05-16"
    assert fm.deciders == ["driller"]
    assert fm.supersedes is None
    assert fm.superseded_by is None
    assert body.strip() == "# ADR-0001: テスト決定"


def test_dump_frontmatter_roundtrips():
    fm, body = parse_frontmatter(SAMPLE)
    rebuilt = dump_frontmatter(fm) + "\n" + body
    fm2, body2 = parse_frontmatter(rebuilt)
    assert fm2 == fm
    assert body2 == body


def test_parse_frontmatter_rejects_missing_block():
    with __import__("pytest").raises(AdrError):
        parse_frontmatter("# no frontmatter here\n")
```

- [ ] **Step 2: テストが失敗することを確認**

Run: `uv run pytest tests/test_adrlib.py -v`
Expected: FAIL（`ModuleNotFoundError: No module named 'adrlib'`）

- [ ] **Step 3: `adrlib.py` の最小実装**

`skills/adr-author/scripts/adrlib.py`:

```python
"""ADR ファイルのフロントマターと採番を扱う共有ユーティリティ（標準ライブラリのみ）。"""

from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path

ADR_FILENAME_RE = re.compile(r"^(\d{4})-[a-z0-9-]+\.md$")
SLUG_RE = re.compile(r"^[a-z0-9-]+$")


class AdrError(Exception):
    """ADR 操作の明示的エラー。フォールバックせず送出する。"""


@dataclass
class Frontmatter:
    adr: str
    title: str
    status: str
    date: str
    deciders: list[str]
    supersedes: str | None = None
    superseded_by: str | None = None


def _strip_quotes(value: str) -> str:
    value = value.strip()
    if len(value) >= 2 and value[0] == value[-1] and value[0] in "\"'":
        return value[1:-1]
    return value


def _scalar_or_none(value: str) -> str | None:
    value = value.strip()
    if value == "null":
        return None
    return _strip_quotes(value)


def parse_frontmatter(text: str) -> tuple[Frontmatter, str]:
    """`---` で囲われた固定スキーマのフロントマターと本文を返す。"""
    if not text.startswith("---\n"):
        raise AdrError("フロントマターが見つかりません（先頭に '---' が必要）。")
    end = text.find("\n---\n", 4)
    if end == -1:
        raise AdrError("フロントマターの終端 '---' が見つかりません。")
    block = text[4:end]
    body = text[end + 5 :]
    scalars: dict[str, str] = {}
    deciders: list[str] = []
    current_list: str | None = None
    for line in block.splitlines():
        if not line.strip():
            continue
        if line.startswith("  - ") and current_list == "deciders":
            deciders.append(_strip_quotes(line[4:]))
            continue
        key, _, value = line.partition(":")
        key = key.strip()
        if value.strip() == "" and key == "deciders":
            current_list = "deciders"
            continue
        current_list = None
        scalars[key] = value
    required = ("adr", "title", "status", "date")
    for field_name in required:
        if field_name not in scalars:
            raise AdrError(f"フロントマターに必須キー '{field_name}' がありません。")
    return (
        Frontmatter(
            adr=_strip_quotes(scalars["adr"]),
            title=_strip_quotes(scalars["title"]),
            status=scalars["status"].strip(),
            date=scalars["date"].strip(),
            deciders=deciders,
            supersedes=_scalar_or_none(scalars.get("supersedes", "null")),
            superseded_by=_scalar_or_none(scalars.get("superseded_by", "null")),
        ),
        body,
    )


def dump_frontmatter(fm: Frontmatter) -> str:
    """Frontmatter を `---` で囲った文字列に直す。"""
    lines = [
        "---",
        f'adr: "{fm.adr}"',
        f'title: "{fm.title}"',
        f"status: {fm.status}",
        f"date: {fm.date}",
        "deciders:",
    ]
    lines += [f"  - {d}" for d in fm.deciders]
    lines.append(f'supersedes: {fm.supersedes if fm.supersedes else "null"}')
    lines.append(
        f'superseded_by: {fm.superseded_by if fm.superseded_by else "null"}'
    )
    lines.append("---")
    return "\n".join(lines)


def next_number(adr_dir: Path) -> str:
    """`adr_dir` 内の最大 ADR 番号 +1 を 4 桁ゼロ埋めで返す。"""
    numbers = [
        int(m.group(1))
        for p in adr_dir.glob("*.md")
        if (m := ADR_FILENAME_RE.match(p.name))
    ]
    return f"{(max(numbers) + 1) if numbers else 1:04d}"
```

- [ ] **Step 4: テストが通ることを確認**

Run: `uv run pytest tests/test_adrlib.py -v`
Expected: PASS（3 件）

- [ ] **Step 5: 採番テストを追加して失敗を確認**

`tests/test_adrlib.py` に追記:

```python
def test_next_number_empty_dir_returns_0001(tmp_path):
    assert next_number(tmp_path) == "0001"


def test_next_number_skips_non_adr_files(tmp_path):
    (tmp_path / "0001-a.md").write_text("x")
    (tmp_path / "0007-b.md").write_text("x")
    (tmp_path / "index.md").write_text("x")
    (tmp_path / "architecture-overview.md").write_text("x")
    assert next_number(tmp_path) == "0008"
```

Run: `uv run pytest tests/test_adrlib.py -v` → 既存実装で PASS するはず（`next_number` は Step 3 で実装済み）。PASS を確認する。

- [ ] **Step 6: 品質チェックとコミット**

```bash
uv run ruff check --fix . && uv run ruff format . && uv run mypy .
git add skills/adr-author/scripts/adrlib.py tests/test_adrlib.py
git commit -m "feat: add adrlib frontmatter and numbering helpers"
```

---

## Task 4: `create_adr.py` — ADR ファイル生成（TDD）

**Files:**
- Create: `tests/test_create_adr.py`
- Create: `skills/adr-author/scripts/create_adr.py`

`create_adr.py` の責務: `<adr-dir>/_templates/adr_template.md` を読み、次番号・タイトル・slug・deciders・spec を埋めて `<adr-dir>/NNNN-slug.md` を生成する。`status` は常に `Proposed`。`index.md` は編集しない（glob toctree）。

引数: `--adr-dir`（必須）、`--title`（必須・表示用、日本語可）、`--slug`（必須・`[a-z0-9-]+`）、`--decider`（必須・複数可）、`--spec`（任意）、`--date`（任意・既定は当日）。

- [ ] **Step 1: 失敗するテストを書く**

`tests/test_create_adr.py`:

```python
import pytest

from adrlib import AdrError, parse_frontmatter
from create_adr import create_adr

TEMPLATE = (
    '---\n'
    'adr: "{{ADR}}"\n'
    'title: "{{TITLE}}"\n'
    'status: Proposed\n'
    'date: {{DATE}}\n'
    'deciders:\n'
    '{{DECIDERS}}\n'
    'supersedes: null\n'
    'superseded_by: null\n'
    '---\n'
    '\n'
    '# ADR-{{ADR}}: {{TITLE}}\n'
    '\n'
    '## 関連ドキュメント\n'
    '\n'
    '- spec: {{SPEC}}\n'
)


@pytest.fixture
def adr_dir(tmp_path):
    templates = tmp_path / "_templates"
    templates.mkdir()
    (templates / "adr_template.md").write_text(TEMPLATE, encoding="utf-8")
    return tmp_path


def test_create_adr_writes_numbered_file(adr_dir):
    path = create_adr(
        adr_dir=adr_dir,
        title="2 層モデルを採用する",
        slug="two-layer-model",
        deciders=["driller"],
        spec="docs/superpowers/specs/2026-05-16-adr-skills-design.md",
        date="2026-05-16",
    )
    assert path == adr_dir / "0001-two-layer-model.md"
    fm, body = parse_frontmatter(path.read_text(encoding="utf-8"))
    assert fm.adr == "0001"
    assert fm.title == "2 層モデルを採用する"
    assert fm.status == "Proposed"
    assert fm.deciders == ["driller"]
    assert "docs/superpowers/specs/2026-05-16-adr-skills-design.md" in body


def test_create_adr_increments_number(adr_dir):
    (adr_dir / "0001-x.md").write_text("placeholder", encoding="utf-8")
    path = create_adr(
        adr_dir=adr_dir, title="次の決定", slug="next-one",
        deciders=["driller"], spec=None, date="2026-05-16",
    )
    assert path.name == "0002-next-one.md"


def test_create_adr_rejects_bad_slug(adr_dir):
    with pytest.raises(AdrError):
        create_adr(
            adr_dir=adr_dir, title="X", slug="Bad_Slug",
            deciders=["driller"], spec=None, date="2026-05-16",
        )


def test_create_adr_rejects_missing_template(tmp_path):
    with pytest.raises(AdrError):
        create_adr(
            adr_dir=tmp_path, title="X", slug="x",
            deciders=["driller"], spec=None, date="2026-05-16",
        )
```

- [ ] **Step 2: テストが失敗することを確認**

Run: `uv run pytest tests/test_create_adr.py -v`
Expected: FAIL（`ModuleNotFoundError: No module named 'create_adr'`）

- [ ] **Step 3: `create_adr.py` を実装**

```python
"""ADR ファイルを雛形から生成する（第 1 層スクリプト）。"""

from __future__ import annotations

import argparse
import datetime
from pathlib import Path

from adrlib import SLUG_RE, AdrError, next_number


def create_adr(
    *,
    adr_dir: Path,
    title: str,
    slug: str,
    deciders: list[str],
    spec: str | None,
    date: str,
) -> Path:
    """`adr_dir` に新規 ADR ファイルを作成し、そのパスを返す。"""
    if not SLUG_RE.match(slug):
        raise AdrError(f"slug は [a-z0-9-]+ である必要があります: {slug!r}")
    if not deciders:
        raise AdrError("deciders を 1 つ以上指定してください。")
    template_path = adr_dir / "_templates" / "adr_template.md"
    if not template_path.is_file():
        raise AdrError(f"テンプレートが見つかりません: {template_path}")
    number = next_number(adr_dir)
    out_path = adr_dir / f"{number}-{slug}.md"
    if out_path.exists():
        raise AdrError(f"既に存在します: {out_path}")
    text = template_path.read_text(encoding="utf-8")
    text = (
        text.replace("{{ADR}}", number)
        .replace("{{TITLE}}", title)
        .replace("{{DATE}}", date)
        .replace("{{DECIDERS}}", "\n".join(f"  - {d}" for d in deciders))
        .replace("{{SPEC}}", spec if spec else "なし")
    )
    out_path.write_text(text, encoding="utf-8")
    return out_path


def main() -> None:
    parser = argparse.ArgumentParser(description="新規 ADR を生成する。")
    parser.add_argument("--adr-dir", required=True, type=Path)
    parser.add_argument("--title", required=True)
    parser.add_argument("--slug", required=True)
    parser.add_argument("--decider", required=True, action="append", dest="deciders")
    parser.add_argument("--spec", default=None)
    parser.add_argument(
        "--date", default=datetime.date.today().isoformat()
    )
    args = parser.parse_args()
    path = create_adr(
        adr_dir=args.adr_dir,
        title=args.title,
        slug=args.slug,
        deciders=args.deciders,
        spec=args.spec,
        date=args.date,
    )
    print(path)


if __name__ == "__main__":
    main()
```

- [ ] **Step 4: テストが通ることを確認**

Run: `uv run pytest tests/test_create_adr.py -v`
Expected: PASS（4 件）

- [ ] **Step 5: 品質チェックとコミット**

```bash
uv run ruff check --fix . && uv run ruff format . && uv run mypy .
git add skills/adr-author/scripts/create_adr.py tests/test_create_adr.py
git commit -m "feat: add create_adr script"
```

---

## Task 5: `set_status.py` — status 遷移（TDD）

**Files:**
- Create: `tests/test_set_status.py`
- Create: `skills/adr-author/scripts/set_status.py`

`set_status.py` の責務: 指定 ADR のフロントマター `status` を遷移させる。許可遷移は `Proposed → Accepted`、`Proposed → Deprecated`、`Accepted → Deprecated` のみ。`Superseded` への遷移は `supersede.py` の責務であり拒否する。

引数: `--adr-dir`（必須）、`--number`（必須・4 桁）、`--status`（必須）。

- [ ] **Step 1: 失敗するテストを書く**

`tests/test_set_status.py`:

```python
import pytest

from adrlib import AdrError, parse_frontmatter
from set_status import set_status

ADR = (
    '---\n'
    'adr: "0001"\n'
    'title: "X"\n'
    'status: Proposed\n'
    'date: 2026-05-16\n'
    'deciders:\n'
    '  - driller\n'
    'supersedes: null\n'
    'superseded_by: null\n'
    '---\n'
    '\n'
    '# ADR-0001: X\n'
)


@pytest.fixture
def adr_dir(tmp_path):
    (tmp_path / "0001-x.md").write_text(ADR, encoding="utf-8")
    return tmp_path


def test_set_status_proposed_to_accepted(adr_dir):
    set_status(adr_dir=adr_dir, number="0001", status="Accepted")
    fm, _ = parse_frontmatter((adr_dir / "0001-x.md").read_text(encoding="utf-8"))
    assert fm.status == "Accepted"


def test_set_status_rejects_superseded(adr_dir):
    with pytest.raises(AdrError):
        set_status(adr_dir=adr_dir, number="0001", status="Superseded")


def test_set_status_rejects_unknown_status(adr_dir):
    with pytest.raises(AdrError):
        set_status(adr_dir=adr_dir, number="0001", status="Done")


def test_set_status_rejects_missing_adr(adr_dir):
    with pytest.raises(AdrError):
        set_status(adr_dir=adr_dir, number="0099", status="Accepted")
```

- [ ] **Step 2: テストが失敗することを確認**

Run: `uv run pytest tests/test_set_status.py -v`
Expected: FAIL（`ModuleNotFoundError: No module named 'set_status'`）

- [ ] **Step 3: `adrlib.py` に ADR 検索・読み書きヘルパを追加**

`skills/adr-author/scripts/adrlib.py` の末尾に追加:

```python
def find_adr(adr_dir: Path, number: str) -> Path:
    """番号に対応する ADR ファイルパスを返す。無ければ AdrError。"""
    matches = sorted(adr_dir.glob(f"{number}-*.md"))
    if not matches:
        raise AdrError(f"ADR-{number} が {adr_dir} に見つかりません。")
    if len(matches) > 1:
        raise AdrError(f"ADR-{number} が複数あります: {[p.name for p in matches]}")
    return matches[0]


def read_adr(path: Path) -> tuple[Frontmatter, str]:
    return parse_frontmatter(path.read_text(encoding="utf-8"))


def write_adr(path: Path, fm: Frontmatter, body: str) -> None:
    path.write_text(dump_frontmatter(fm) + body, encoding="utf-8")
```

注: `parse_frontmatter` は本文を先頭の `\n` 込みで返すため、`write_adr` は `dump_frontmatter(fm) + body` で元の体裁を保つ。

- [ ] **Step 4: `set_status.py` を実装**

```python
"""ADR の status を遷移させる（第 1 層スクリプト）。"""

from __future__ import annotations

import argparse
from pathlib import Path

from adrlib import AdrError, find_adr, read_adr, write_adr

ALLOWED_TRANSITIONS = {
    ("Proposed", "Accepted"),
    ("Proposed", "Deprecated"),
    ("Accepted", "Deprecated"),
}


def set_status(*, adr_dir: Path, number: str, status: str) -> None:
    """ADR-`number` の status を `status` に遷移させる。"""
    if status == "Superseded":
        raise AdrError("Superseded への遷移は supersede.py を使ってください。")
    path = find_adr(adr_dir, number)
    fm, body = read_adr(path)
    if (fm.status, status) not in ALLOWED_TRANSITIONS:
        raise AdrError(f"許可されない遷移です: {fm.status} -> {status}")
    fm.status = status
    write_adr(path, fm, body)


def main() -> None:
    parser = argparse.ArgumentParser(description="ADR の status を遷移させる。")
    parser.add_argument("--adr-dir", required=True, type=Path)
    parser.add_argument("--number", required=True)
    parser.add_argument("--status", required=True)
    args = parser.parse_args()
    set_status(adr_dir=args.adr_dir, number=args.number, status=args.status)
    print(f"ADR-{args.number} -> {args.status}")


if __name__ == "__main__":
    main()
```

- [ ] **Step 5: テストが通ることを確認**

Run: `uv run pytest tests/test_set_status.py tests/test_adrlib.py -v`
Expected: PASS（set_status 4 件 + adrlib 既存 5 件）

- [ ] **Step 6: 品質チェックとコミット**

```bash
uv run ruff check --fix . && uv run ruff format . && uv run mypy .
git add skills/adr-author/scripts/adrlib.py skills/adr-author/scripts/set_status.py tests/test_set_status.py
git commit -m "feat: add set_status script and adr lookup helpers"
```

---

## Task 6: `supersede.py` — supersede 相互リンク（TDD）

**Files:**
- Create: `tests/test_supersede.py`
- Create: `skills/adr-author/scripts/supersede.py`

`supersede.py` の責務: 旧 ADR の `status` を `Superseded`・`superseded_by` を新番号に、新 ADR の `supersedes` を旧番号に設定する。両 ADR が存在し、旧 ADR がまだ `Superseded` でないことを検証する。旧ファイルは削除しない。

引数: `--adr-dir`（必須）、`--number`（必須・旧）、`--by`（必須・新）。

- [ ] **Step 1: 失敗するテストを書く**

`tests/test_supersede.py`:

```python
import pytest

from adrlib import AdrError, parse_frontmatter
from supersede import supersede


def _adr(number: str, status: str = "Accepted") -> str:
    return (
        '---\n'
        f'adr: "{number}"\n'
        'title: "X"\n'
        f'status: {status}\n'
        'date: 2026-05-16\n'
        'deciders:\n'
        '  - driller\n'
        'supersedes: null\n'
        'superseded_by: null\n'
        '---\n'
        '\n'
        f'# ADR-{number}: X\n'
    )


@pytest.fixture
def adr_dir(tmp_path):
    (tmp_path / "0001-old.md").write_text(_adr("0001"), encoding="utf-8")
    (tmp_path / "0002-new.md").write_text(_adr("0002", "Proposed"), encoding="utf-8")
    return tmp_path


def test_supersede_links_both_adrs(adr_dir):
    supersede(adr_dir=adr_dir, number="0001", by="0002")
    old, _ = parse_frontmatter((adr_dir / "0001-old.md").read_text(encoding="utf-8"))
    new, _ = parse_frontmatter((adr_dir / "0002-new.md").read_text(encoding="utf-8"))
    assert old.status == "Superseded"
    assert old.superseded_by == "0002"
    assert new.supersedes == "0001"


def test_supersede_keeps_old_file(adr_dir):
    supersede(adr_dir=adr_dir, number="0001", by="0002")
    assert (adr_dir / "0001-old.md").exists()


def test_supersede_rejects_already_superseded(adr_dir):
    supersede(adr_dir=adr_dir, number="0001", by="0002")
    with pytest.raises(AdrError):
        supersede(adr_dir=adr_dir, number="0001", by="0002")


def test_supersede_rejects_missing_adr(adr_dir):
    with pytest.raises(AdrError):
        supersede(adr_dir=adr_dir, number="0001", by="0099")
```

- [ ] **Step 2: テストが失敗することを確認**

Run: `uv run pytest tests/test_supersede.py -v`
Expected: FAIL（`ModuleNotFoundError: No module named 'supersede'`）

- [ ] **Step 3: `supersede.py` を実装**

```python
"""ADR の supersede 関係を設定する（第 1 層スクリプト）。"""

from __future__ import annotations

import argparse
from pathlib import Path

from adrlib import AdrError, find_adr, read_adr, write_adr


def supersede(*, adr_dir: Path, number: str, by: str) -> None:
    """ADR-`number` を ADR-`by` で supersede する。"""
    old_path = find_adr(adr_dir, number)
    new_path = find_adr(adr_dir, by)
    old_fm, old_body = read_adr(old_path)
    new_fm, new_body = read_adr(new_path)
    if old_fm.status == "Superseded":
        raise AdrError(f"ADR-{number} は既に Superseded です。")
    old_fm.status = "Superseded"
    old_fm.superseded_by = by
    new_fm.supersedes = number
    write_adr(old_path, old_fm, old_body)
    write_adr(new_path, new_fm, new_body)


def main() -> None:
    parser = argparse.ArgumentParser(description="ADR を supersede する。")
    parser.add_argument("--adr-dir", required=True, type=Path)
    parser.add_argument("--number", required=True)
    parser.add_argument("--by", required=True)
    args = parser.parse_args()
    supersede(adr_dir=args.adr_dir, number=args.number, by=args.by)
    print(f"ADR-{args.number} superseded by ADR-{args.by}")


if __name__ == "__main__":
    main()
```

- [ ] **Step 4: テストが通ることを確認**

Run: `uv run pytest tests/test_supersede.py -v`
Expected: PASS（4 件）

- [ ] **Step 5: 品質チェックとコミット**

```bash
uv run ruff check --fix . && uv run ruff format . && uv run mypy .
git add skills/adr-author/scripts/supersede.py tests/test_supersede.py
git commit -m "feat: add supersede script"
```

---

## Task 7: `check_adr.py` — spec と ADR の対応点検（TDD）

**Files:**
- Create: `tests/test_check_adr.py`
- Create: `skills/adr-author/scripts/check_adr.py`

`check_adr.py` の責務: `specs_dir` 内の `*-design.md` のうち、どの ADR の本文からも参照されていないものを列挙する。ADR 本文中の `docs/superpowers/specs/....md` 形式のパスを参照とみなす。生成は行わない。未参照があれば終了コード 1、無ければ 0。

引数: `--adr-dir`（必須）、`--specs-dir`（必須）。

- [ ] **Step 1: 失敗するテストを書く**

`tests/test_check_adr.py`:

```python
from check_adr import find_unrecorded_specs


def _write(path, text):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def test_find_unrecorded_specs_reports_missing(tmp_path):
    adr_dir = tmp_path / "adr"
    specs_dir = tmp_path / "specs"
    _write(specs_dir / "2026-01-01-alpha-design.md", "# alpha")
    _write(specs_dir / "2026-02-02-beta-design.md", "# beta")
    _write(
        adr_dir / "0001-a.md",
        "# ADR\n- spec: docs/superpowers/specs/2026-01-01-alpha-design.md\n",
    )
    unrecorded = find_unrecorded_specs(adr_dir=adr_dir, specs_dir=specs_dir)
    assert unrecorded == [specs_dir / "2026-02-02-beta-design.md"]


def test_find_unrecorded_specs_empty_when_all_recorded(tmp_path):
    adr_dir = tmp_path / "adr"
    specs_dir = tmp_path / "specs"
    _write(specs_dir / "2026-01-01-alpha-design.md", "# alpha")
    _write(
        adr_dir / "0001-a.md",
        "# ADR\n- spec: docs/superpowers/specs/2026-01-01-alpha-design.md\n",
    )
    assert find_unrecorded_specs(adr_dir=adr_dir, specs_dir=specs_dir) == []
```

- [ ] **Step 2: テストが失敗することを確認**

Run: `uv run pytest tests/test_check_adr.py -v`
Expected: FAIL（`ModuleNotFoundError: No module named 'check_adr'`）

- [ ] **Step 3: `check_adr.py` を実装**

```python
"""spec と ADR の対応を点検する（第 1 層スクリプト）。生成は行わない。"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path


def find_unrecorded_specs(*, adr_dir: Path, specs_dir: Path) -> list[Path]:
    """どの ADR からも参照されていない design spec を返す。"""
    referenced: set[str] = set()
    if adr_dir.is_dir():
        for adr in adr_dir.glob("[0-9][0-9][0-9][0-9]-*.md"):
            text = adr.read_text(encoding="utf-8")
            for spec in specs_dir.glob("*-design.md"):
                if spec.name in text:
                    referenced.add(spec.name)
    unrecorded = [
        spec
        for spec in sorted(specs_dir.glob("*-design.md"))
        if spec.name not in referenced
    ]
    return unrecorded


def main() -> None:
    parser = argparse.ArgumentParser(description="spec と ADR の対応を点検する。")
    parser.add_argument("--adr-dir", required=True, type=Path)
    parser.add_argument("--specs-dir", required=True, type=Path)
    args = parser.parse_args()
    unrecorded = find_unrecorded_specs(adr_dir=args.adr_dir, specs_dir=args.specs_dir)
    if unrecorded:
        print("ADR 未記録の spec:")
        for spec in unrecorded:
            print(f"  - {spec}")
        sys.exit(1)
    print("すべての spec が ADR に対応しています。")


if __name__ == "__main__":
    main()
```

- [ ] **Step 4: テストが通ることを確認**

Run: `uv run pytest tests/ -v`
Expected: PASS（全テストファイル）

- [ ] **Step 5: 品質チェックとコミット**

```bash
uv run ruff check --fix . && uv run ruff format . && uv run mypy .
git add skills/adr-author/scripts/check_adr.py tests/test_check_adr.py
git commit -m "feat: add check_adr script"
```

---

## Task 8: `adr-author` スキル本文

**Files:**
- Create: `skills/adr-author/SKILL.md`

- [ ] **Step 1: `SKILL.md` を作成**

YAML フロントマター:

```yaml
---
name: adr-author
description: アーキテクチャ・仕様に関わる決定を ADR (Architecture Decision Record) として記録する。superpowers の design spec (docs/superpowers/specs/*-design.md) が書かれた直後、またはフレームワーク・ライブラリ・境界・プロトコル・データ構造の選定で代替案を伴う決定が確定した場面、または「ADR を書いて」と明示依頼された場面で発火する。バグ修正・リファクタリング・ドキュメント更新など決定を伴わない作業では発火しない。
license: MIT
allowed-tools: Bash, Read, Write, Edit, Glob, Grep
---
```

本文に以下を記述:

- **ベストプラクティス**（スペックの「ベストプラクティス」節の 6 項目をそのまま記載: 1 ADR=1 決定、Accepted 後は不変、status 遷移、代替案・トレードオフを正直に、MADR 系フロントマター、出典抜粋の凍結）。
- **ワークフロー**（スペックの adr-author ワークフロー 1〜5）。特に **手順 3 の合意ゲート**を強調: ユーザーに「ADR-NNNN としてこう記録します」とプレビュー提示し、ADR 化の要否を含め合意を得てから手順 4 に進む。
- **スクリプトの呼び出し方**（`uv run python skills/.../scripts/...` ではなく、スキルバンドル内の相対パスで呼ぶ。スキル配置先からの相対で `scripts/create_adr.py` を `python` で実行）:
  - 新規: `python scripts/create_adr.py --adr-dir <dir> --title <t> --slug <s> --decider <name> [--spec <path>]`
  - status: `python scripts/set_status.py --adr-dir <dir> --number <NNNN> --status <S>`
  - supersede: `python scripts/supersede.py --adr-dir <dir> --number <NNNN> --by <MMMM>`
  - 点検: `python scripts/check_adr.py --adr-dir <dir> --specs-dir <dir>`
- **未初期化の扱い**: ADR ディレクトリ（`index.md` と `_templates/adr_template.md`）が無い場合は暗黙に進めず、`adr-init` の実行を促す。
- **機密保持**: 他者プロジェクトの決定内容をスキルパッケージや外部へ出さない。

- [ ] **Step 2: コミット**

```bash
git add skills/adr-author/SKILL.md
git commit -m "feat: add adr-author skill"
```

---

## Task 9: `adr-init` スキル本文

**Files:**
- Create: `skills/adr-init/SKILL.md`

- [ ] **Step 1: `SKILL.md` を作成**

YAML フロントマター:

```yaml
---
name: adr-init
description: ADR (Architecture Decision Record) の置き場を Sphinx プロジェクトに用意する。「ADR 管理を始めたい」「ADR を初期化」と依頼された場面で発火する。既存 Sphinx プロジェクトがあればその配下に ADR セクションを追加し、無ければ ADR 専用の Sphinx プロジェクトを新規生成する。
license: MIT
allowed-tools: Bash, Read, Write, Edit, Glob
---
```

本文に以下を記述:

- **モード判定**: 対象リポジトリに `conf.py` を持つ Sphinx プロジェクトがあるか Glob で確認する。
- **セクション追加モード**（既存 `conf.py` あり）:
  1. ADR セクションディレクトリ `<sphinx-root>/adr/` を作る。
  2. `templates/index.md` を `<sphinx-root>/adr/index.md` として配置（glob toctree 付き）。
  3. `templates/adr_template.md` を `<sphinx-root>/adr/_templates/adr_template.md` として配置。
  4. 親 `index.md` の `{toctree}` に `adr/index` を 1 度だけ追加（既にあれば何もしない）。
  5. 親 `conf.py` の `exclude_patterns` に `'adr/_templates'` を追加（無ければ）。`myst_parser` が `extensions` に無ければ `sphinx-config` スキルでの追加を提案する。
- **スタンドアロンモード**（既存 Sphinx プロジェクトなし）:
  1. 配置先を決める（既定 `docs/adr/`、ユーザー指定で上書き可）。
  2. `templates/` の全ファイル（`conf.py` / `index.md` / `Makefile` / `make.bat` / `_static/`）を配置先へコピーし、`_templates/adr_template.md` も配置。
  3. `conf.py` の `{{PROJECT}}` / `{{AUTHOR}}` を埋める。
- **共通**: 完了後、`adr-author` で最初の ADR を起票できる旨を案内する。Sphinx のビルド・テーマ運用は `sphinx-skills` を案内する（ハード依存にしない）。

- [ ] **Step 2: コミット**

```bash
git add skills/adr-init/SKILL.md
git commit -m "feat: add adr-init skill"
```

---

## Task 10: ドッグフーディング — `docs/adr/` セクションのブートストラップ

**Files:**
- Create: `docs/adr/index.md`
- Create: `docs/adr/_templates/adr_template.md`
- Modify: `docs/conf.py:45`（`exclude_patterns`）
- Modify: `docs/index.md`（`{toctree}`）

これは `adr-init` のセクション追加モードを**手動で**実行する作業（スクリプト・スキル完成後の最初の実利用）。

- [ ] **Step 1: `docs/adr/index.md` を配置**

`skills/adr-init/templates/index.md` の内容をそのまま `docs/adr/index.md` にコピーする。

- [ ] **Step 2: `docs/adr/_templates/adr_template.md` を配置**

`skills/adr-init/templates/adr_template.md` の内容をそのまま `docs/adr/_templates/adr_template.md` にコピーする。

- [ ] **Step 3: `docs/conf.py` の `exclude_patterns` を更新**

`docs/conf.py:45` を次のように変更（`adr/_templates` を追加。これにより ADR スケルトンがビルドされない）:

```python
exclude_patterns = ['_build', 'Thumbs.db', '.DS_Store', 'superpowers', 'adr/_templates']
```

- [ ] **Step 4: `docs/index.md` の toctree に `adr/index` を追加**

`docs/index.md` の空の `{toctree}` を次のように変更:

```markdown
```{toctree}
:maxdepth: 2
:caption: Contents:

adr/index
```
```

- [ ] **Step 5: Sphinx ビルドで警告が出ないことを確認**

Run: `cd docs && uv run sphinx-build -W -b html . _build/html && cd ..`
Expected: 警告ゼロでビルド成功（`-W` で警告をエラー化）。ADR ファイルがまだ無いため `index` の toctree は空でよい。

- [ ] **Step 6: コミット**

```bash
git add docs/adr/index.md docs/adr/_templates/adr_template.md docs/conf.py docs/index.md
git commit -m "docs: bootstrap docs/adr section (dogfooding)"
```

---

## Task 11: ドッグフーディング — ブレストの決定を ADR として起票

**Files:**
- Create: `docs/adr/0001-*.md` 〜 `docs/adr/0006-*.md`

設計ブレストで確定した決定を、完成した `create_adr.py` で起票し、各 ADR の Context / Decision / Consequences / Alternatives を執筆する。spec は全て `docs/superpowers/specs/2026-05-16-adr-skills-design.md`。

起票する ADR（slug と Decision の要旨）:

| 番号 | slug | Decision の要旨 |
|---|---|---|
| 0001 | `two-layer-architecture` | 決定的処理（スクリプト）と合意ベースの起草（スキル）を 2 層に分離する |
| 0002 | `scripts-not-cli` | 第 1 層を `adr` CLI でなくスキル同梱スクリプトで実装する |
| 0003 | `trigger-by-skill-not-hook` | 自動記録の発火は hook でなくスキル description とし、記録には合意ゲートを必須とする |
| 0004 | `no-vendoring` | 第 1 層スクリプトを利用側リポジトリへ vendoring せず、スキルバンドル内から動作させる |
| 0005 | `adr-init-dual-mode` | `adr-init` をセクション追加／スタンドアロンの 2 モードにする |
| 0006 | `glob-toctree` | ADR 索引の toctree は `:glob:` で自動収集し、スクリプトは `index.md` を編集しない |

- [ ] **Step 1: ADR-0001 を起票**

Run:
```bash
python skills/adr-author/scripts/create_adr.py \
  --adr-dir docs/adr --title "決定的処理と起草を 2 層に分離する" \
  --slug two-layer-architecture --decider driller \
  --spec docs/superpowers/specs/2026-05-16-adr-skills-design.md
```
生成された `docs/adr/0001-two-layer-architecture.md` の Context / Decision / Consequences / Alternatives を、spec の「アーキテクチャ：2 層モデル」節に基づいて執筆する。「決定時の参考資料（抜粋）」に spec の該当箇所を引用ブロックで貼り付け凍結する。

- [ ] **Step 2: ADR-0002 〜 0006 を同様に起票・執筆**

各行について Step 1 と同じ手順（`create_adr.py` 実行 → 本文執筆）。slug・title・Decision 要旨は上表のとおり。各 ADR の Alternatives Considered には、却下した案（例: 0002 なら「`adr` CLI 案」、0003 なら「hook 案」「黙って自動生成案」）を見送り理由 1 行付きで記載する。

- [ ] **Step 3: `check_adr.py` で対応を確認**

Run: `python skills/adr-author/scripts/check_adr.py --adr-dir docs/adr --specs-dir docs/superpowers/specs`
Expected: 「すべての spec が ADR に対応しています。」（終了コード 0）

- [ ] **Step 4: Sphinx ビルドで警告ゼロを確認**

Run: `cd docs && uv run sphinx-build -W -b html . _build/html && cd ..`
Expected: 警告ゼロ。`adr/index` の glob toctree に 0001〜0006 が並ぶ。

- [ ] **Step 5: コミット**

```bash
git add docs/adr/0001-*.md docs/adr/0002-*.md docs/adr/0003-*.md docs/adr/0004-*.md docs/adr/0005-*.md docs/adr/0006-*.md
git commit -m "docs: record brainstorming decisions as ADR-0001..0006 (dogfooding)"
```

---

## Task 12: CI ワークフローと README 仕上げ

**Files:**
- Create: `.github/workflows/ci.yml`
- Modify: `README.md`

- [ ] **Step 1: `.github/workflows/ci.yml` を作成**

`ubuntu-latest`、`astral-sh/setup-uv` を使い、`push` と `pull_request` で次を実行:
- `uv run ruff check .`
- `uv run ruff format --check .`
- `uv run mypy .`
- `uv run pytest -v`

- [ ] **Step 2: テストとリンタがローカルで通ることを最終確認**

Run: `uv run ruff check . && uv run ruff format --check . && uv run mypy . && uv run pytest -v`
Expected: すべて PASS

- [ ] **Step 3: `README.md` を仕上げる**

`sphinx-skills` の README を範として、以下を記載:
- 概要、提供スキル表（`adr-init` / `adr-author`）
- インストール: `apm install drillan/adr-skills --target claude`
- 第 1 層スクリプトと 2 層モデルの簡単な説明
- ADR のベストプラクティス参照

機密保持: 他者プロジェクトの名前・パス・決定内容を一切含めないこと。

- [ ] **Step 4: コミット**

```bash
git add .github/workflows/ci.yml README.md
git commit -m "ci: add lint/type/test workflow and finalize README"
```

---

## Self-Review

**Spec coverage:**
- 2 層モデル → Task 3-9（スクリプト = 第 1 層、スキル = 第 2 層）
- 第 1 層スクリプト 4 本 + 共有 `adrlib` → Task 3-7
- 標準ライブラリのみで自己完結 → `adrlib.py` / 各スクリプトに外部 import なし。`pyproject.toml` の依存は dev のみ
- `adr-init` 2 モード → Task 9 / Task 10（手動実行例）
- `adr-author` 発火条件・合意ゲート・ワークフロー → Task 8
- ADR テンプレート・Sphinx テンプレート → Task 2
- APM 配布（`skills/` 配下に同梱）→ ディレクトリ構成どおり。`apm.yml` → Task 1
- ドッグフーディング → Task 10-11
- TDD・1 機能 1 テストファイル → Task 3-7（各スクリプトに対応する `test_*.py`）
- 機密保持 → Task 8 / 11 / 12 に明記
- `check_adr` による安全網 → Task 7 / 11 Step 3

**スペックとの差分（計画段階の精緻化、ヘッダに明記済み）:** `index.md` の toctree 登録は `:glob:` により自動化し、スクリプトは `index.md` を編集しない。スペックの「toctree と一覧に登録」のうち toctree は glob で達成、別建ての「一覧」はフロントマター `status`（GitHub レンダリング）と glob toctree で代替し、スクリプトによる脆弱な構造化編集を排除した。

**Placeholder scan:** プレースホルダ表現なし。テンプレートファイル内の `{{ADR}}` 等はスクリプトが置換する正規のトークンであり、計画上の placeholder ではない。

**Type consistency:** `Frontmatter` のフィールド名（`adr` / `title` / `status` / `date` / `deciders` / `supersedes` / `superseded_by`）は Task 3 で定義し Task 4-7 で一貫使用。`adrlib` の公開シンボル（`parse_frontmatter` / `dump_frontmatter` / `next_number` / `find_adr` / `read_adr` / `write_adr` / `AdrError` / `SLUG_RE`）は定義タスクと利用タスクで名称一致。各スクリプトの処理関数（`create_adr` / `set_status` / `supersede` / `find_unrecorded_specs`）はテストと実装で署名一致。
