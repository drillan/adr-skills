from pathlib import Path

import pytest

from adrlib import AdrError, dump_frontmatter, next_number, parse_frontmatter

SAMPLE = (
    "---\n"
    'adr: "0001"\n'
    'title: "テスト決定"\n'
    "status: Proposed\n"
    "date: 2026-05-16\n"
    "deciders:\n"
    "  - driller\n"
    "supersedes: null\n"
    "superseded_by: null\n"
    "---\n"
    "\n"
    "# ADR-0001: テスト決定\n"
)


def test_parse_frontmatter_reads_all_fields() -> None:
    fm, body = parse_frontmatter(SAMPLE)
    assert fm.adr == "0001"
    assert fm.title == "テスト決定"
    assert fm.status == "Proposed"
    assert fm.date == "2026-05-16"
    assert fm.deciders == ["driller"]
    assert fm.supersedes is None
    assert fm.superseded_by is None
    assert body.strip() == "# ADR-0001: テスト決定"


def test_dump_frontmatter_roundtrips() -> None:
    fm, body = parse_frontmatter(SAMPLE)
    rebuilt = dump_frontmatter(fm) + "\n" + body
    fm2, body2 = parse_frontmatter(rebuilt)
    assert fm2 == fm
    assert body2 == body


def test_parse_frontmatter_rejects_missing_block() -> None:
    with pytest.raises(AdrError):
        parse_frontmatter("# no frontmatter here\n")


def test_dump_frontmatter_roundtrips_with_supersede_links() -> None:
    fm, body = parse_frontmatter(SAMPLE)
    fm.status = "Superseded"
    fm.superseded_by = "0009"
    rebuilt = dump_frontmatter(fm) + "\n" + body
    fm2, _ = parse_frontmatter(rebuilt)
    assert fm2.superseded_by == "0009"
    assert fm2.supersedes is None


def test_next_number_empty_dir_returns_0001(tmp_path: Path) -> None:
    assert next_number(tmp_path) == "0001"


def test_next_number_skips_non_adr_files(tmp_path: Path) -> None:
    (tmp_path / "0001-a.md").write_text("x")
    (tmp_path / "0007-b.md").write_text("x")
    (tmp_path / "index.md").write_text("x")
    (tmp_path / "architecture-overview.md").write_text("x")
    assert next_number(tmp_path) == "0008"
