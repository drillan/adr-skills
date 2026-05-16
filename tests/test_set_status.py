import pytest

from pathlib import Path

from adrlib import AdrError, parse_frontmatter
from set_status import set_status

ADR = (
    "---\n"
    'adr: "0001"\n'
    'title: "X"\n'
    "status: Proposed\n"
    "date: 2026-05-16\n"
    "deciders:\n"
    "  - driller\n"
    "supersedes: null\n"
    "superseded_by: null\n"
    "---\n"
    "\n"
    "# ADR-0001: X\n"
)


@pytest.fixture
def adr_dir(tmp_path: Path) -> Path:
    (tmp_path / "0001-x.md").write_text(ADR, encoding="utf-8")
    return tmp_path


def test_set_status_proposed_to_accepted(adr_dir: Path) -> None:
    set_status(adr_dir=adr_dir, number="0001", status="Accepted")
    fm, _ = parse_frontmatter((adr_dir / "0001-x.md").read_text(encoding="utf-8"))
    assert fm.status == "Accepted"


def test_set_status_rejects_superseded(adr_dir: Path) -> None:
    with pytest.raises(AdrError):
        set_status(adr_dir=adr_dir, number="0001", status="Superseded")


def test_set_status_rejects_unknown_status(adr_dir: Path) -> None:
    with pytest.raises(AdrError):
        set_status(adr_dir=adr_dir, number="0001", status="Done")


def test_set_status_rejects_missing_adr(adr_dir: Path) -> None:
    with pytest.raises(AdrError):
        set_status(adr_dir=adr_dir, number="0099", status="Accepted")


def test_set_status_preserves_body(adr_dir: Path) -> None:
    """書き込み後もフェンスと本文の間の空行が保たれること。"""
    set_status(adr_dir=adr_dir, number="0001", status="Accepted")
    written = (adr_dir / "0001-x.md").read_text(encoding="utf-8")
    assert "---\n\n# ADR-0001: X\n" in written


def test_set_status_is_idempotent_structurally(adr_dir: Path) -> None:
    """2 回 status を変更してもファイル構造が壊れないこと。"""
    set_status(adr_dir=adr_dir, number="0001", status="Accepted")
    set_status(adr_dir=adr_dir, number="0001", status="Deprecated")
    fm, _ = parse_frontmatter((adr_dir / "0001-x.md").read_text(encoding="utf-8"))
    assert fm.status == "Deprecated"
