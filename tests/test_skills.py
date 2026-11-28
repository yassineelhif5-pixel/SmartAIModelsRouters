from __future__ import annotations

import re
import subprocess
import sys
from pathlib import Path
from zipfile import ZipFile

ROOT = Path(__file__).resolve().parents[1]
SKILLS = ROOT / "skills"
HOST_SKILL_ROOTS = (
    ROOT / ".agents" / "skills",
    ROOT / ".claude" / "skills",
    ROOT / ".gemini" / "skills",
    ROOT / ".github" / "skills",
)


def _skill_dirs() -> list[Path]:
    return sorted(
        path for path in SKILLS.iterdir()
        if path.is_dir() and (path / "SKILL.md").is_file()
    )


def test_every_portable_skill_has_valid_frontmatter_and_matching_name() -> None:
    skill_dirs = _skill_dirs()
    assert skill_dirs
    for skill_dir in skill_dirs:
        content = (skill_dir / "SKILL.md").read_text(encoding="utf-8")
        frontmatter = re.match(r"^---\n(?P<body>.*?)\n---\n", content, re.DOTALL)
        assert frontmatter, skill_dir.name
        declared_name = re.search(r"^name:\s*([a-z0-9-]+)\s*$", frontmatter["body"], re.MULTILINE)
        description = re.search(r"^description:\s*(.+)$", frontmatter["body"], re.MULTILINE)
        assert declared_name and declared_name.group(1) == skill_dir.name
        assert description and 20 <= len(description.group(1)) <= 1024


def test_all_host_skill_mirrors_match_canonical_sources() -> None:
    expected_names = {path.name for path in _skill_dirs()}
    for host_root in HOST_SKILL_ROOTS:
        actual_names = {
            path.name for path in host_root.iterdir()
            if path.is_dir() and (path / "SKILL.md").is_file()
        }
        assert actual_names == expected_names, str(host_root)
        for skill_name in expected_names:
            canonical = (SKILLS / skill_name / "SKILL.md").read_bytes()
            mirrored = (host_root / skill_name / "SKILL.md").read_bytes()
            assert mirrored == canonical, f"{host_root}/{skill_name}"


def test_skill_packager_creates_one_valid_archive_per_skill(tmp_path: Path) -> None:
    result = subprocess.run(
        [
            sys.executable,
            str(ROOT / "scripts" / "package-skills.py"),
            "--repo-root",
            str(ROOT),
            "--output-dir",
            str(tmp_path),
        ],
        check=True,
        capture_output=True,
        text=True,
        timeout=20,
    )
    skill_names = {path.name for path in _skill_dirs()}
    archives = {path.stem for path in tmp_path.glob("*.zip")}
    assert archives == skill_names
    assert f"Packaged {len(skill_names)} HIF skills" in result.stdout

    for skill_name in skill_names:
        with ZipFile(tmp_path / f"{skill_name}.zip") as archive:
            member = f"{skill_name}/SKILL.md"
            assert member in archive.namelist()
            assert archive.read(member) == (SKILLS / skill_name / "SKILL.md").read_bytes()
