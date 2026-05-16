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
    lines.append(
        f"supersedes: {fm.supersedes if fm.supersedes is not None else 'null'}"
    )
    lines.append(
        f"superseded_by: {fm.superseded_by if fm.superseded_by is not None else 'null'}"
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
