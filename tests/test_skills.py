from __future__ import annotations

import re
import json
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
    ROOT / ".cursor" / "skills",
    ROOT / ".kimi-code" / "skills",
    ROOT / ".qwen" / "skills",
)


def _skill_dirs() -> list[Path]:
    return sorted(
        path for path in SKILLS.iterdir()
        if path.is_dir() and ".backup." not in path.name and (path / "SKILL.md").is_file()
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
            canonical_root = SKILLS / skill_name
            mirrored_root = host_root / skill_name
            canonical_files = {
                item.relative_to(canonical_root)
                for item in canonical_root.rglob("*") if item.is_file()
            }
            mirrored_files = {
                item.relative_to(mirrored_root)
                for item in mirrored_root.rglob("*") if item.is_file()
            }
            assert mirrored_files == canonical_files, f"{host_root}/{skill_name} file set"
            for relative in canonical_files:
                assert (mirrored_root / relative).read_bytes() == (
                    canonical_root / relative
                ).read_bytes(), f"{host_root}/{skill_name}/{relative}"


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


def test_shell_installer_copies_all_skills_and_backups_existing_install(tmp_path: Path) -> None:
    import os
    import shutil

    bash = shutil.which("bash")
    if bash is None:
        import pytest
        pytest.skip("bash is not installed on this runner")

    home = tmp_path / "home"
    destinations = [
        home / ".claude" / "skills",
        home / ".agents" / "skills",
        home / ".gemini" / "skills",
        home / ".cursor" / "skills",
        home / ".kimi-code" / "skills",
        home / ".qwen" / "skills",
    ]
    destination = destinations[1]
    existing = destination / "hif"
    existing.mkdir(parents=True)
    (existing / "SKILL.md").write_text("user-owned previous skill", encoding="utf-8")
    env = os.environ.copy()
    env["HOME"] = str(home)

    command = [
        bash,
        str(ROOT / "scripts" / "install-hif-skills.sh"),
        "--hosts",
        "claude,codex,gemini,cursor,kimi,qwen",
    ]
    first = subprocess.run(command, env=env, capture_output=True, text=True, timeout=20)
    assert first.returncode == 0, first.stderr

    expected_names = {path.name for path in _skill_dirs()}
    for host_destination in destinations:
        installed_names = {
            path.name for path in host_destination.iterdir()
            if path.is_dir() and ".backup." not in path.name and (path / "SKILL.md").is_file()
        }
        assert installed_names == expected_names
        assert (host_destination / "hif" / "SKILL.md").read_bytes() == (SKILLS / "hif" / "SKILL.md").read_bytes()
    backups = list(destination.glob("hif.backup.*"))
    assert len(backups) == 1
    assert (backups[0] / "SKILL.md").read_text(encoding="utf-8") == "user-owned previous skill"

    second = subprocess.run(command, env=env, capture_output=True, text=True, timeout=20)
    assert second.returncode == 0, second.stderr
    assert len(list(destination.glob("hif.backup.*"))) == 2


def test_every_skill_implements_the_portable_delivery_contract() -> None:
    required = (
        "HIF portable delivery contract",
        "Fast-first interaction",
        "Capability and execution truth",
        "Standard report format",
        "Final quality gate",
    )
    for skill_dir in _skill_dirs():
        content = (skill_dir / "SKILL.md").read_text(encoding="utf-8")
        for phrase in required:
            assert phrase in content, f"{skill_dir.name} missing {phrase}"
        assert "Proposed workflow" in content
        assert "Markdown is the portable default" in content


def test_powershell_installer_accepts_new_hosts_in_whatif_mode() -> None:
    import shutil
    import pytest

    pwsh = shutil.which("pwsh")
    if pwsh is None:
        pytest.skip("PowerShell 7 is not installed on this runner")
    script_path = str(ROOT / "scripts" / "install-hif-skills.ps1").replace("'", "''")
    command = f"& '{script_path}' -Hosts @('Cursor', 'Kimi', 'Qwen') -WhatIf"
    result = subprocess.run(
        [pwsh, "-NoProfile", "-Command", command],
        capture_output=True,
        text=True,
        timeout=30,
    )
    assert result.returncode == 0, result.stderr
    assert "What if:" in result.stdout


def test_portable_plugin_manifest_marketplace_and_bundled_modules() -> None:
    plugin_root = ROOT / "plugins" / "hif-universal"
    manifest = json.loads((plugin_root / "plugin.json").read_text(encoding="utf-8"))
    marketplace = json.loads(
        (ROOT / ".agents" / "plugins" / "marketplace.json").read_text(encoding="utf-8")
    )
    assert manifest["name"] == "hif-universal"
    assert manifest["extensions"]["com.openai"]["onboardingSkill"] == "./skills/hif/SKILL.md"
    assert marketplace["plugins"][0]["source"]["path"] == "./plugins/hif-universal"

    for skill_dir in _skill_dirs():
        bundled = plugin_root / "skills" / skill_dir.name / "SKILL.md"
        assert bundled.is_file(), skill_dir.name
        assert bundled.read_bytes() == (skill_dir / "SKILL.md").read_bytes()

    module_names = {item.name for item in (SKILLS / "hif" / "modules").glob("*.md")}
    bundled_modules = plugin_root / "skills" / "hif" / "modules"
    assert {item.name for item in bundled_modules.glob("*.md")} == module_names
    for module_name in module_names:
        assert (bundled_modules / module_name).read_bytes() == (
            SKILLS / "hif" / "modules" / module_name
        ).read_bytes()
