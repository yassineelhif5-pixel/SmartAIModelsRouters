#!/usr/bin/env python3
"""Build ZIP packages for every portable HIF skill."""
from __future__ import annotations

import argparse
from pathlib import Path
from zipfile import ZIP_DEFLATED, ZipFile


def discover_skills(repo_root: Path) -> list[str]:
    skills_root = repo_root / "skills"
    return sorted(
        item.name
        for item in skills_root.iterdir()
        if item.is_dir() and (item / "SKILL.md").is_file()
    )


def package_skill(repo_root: Path, skill_name: str, output_dir: Path) -> Path:
    source_dir = repo_root / "skills" / skill_name
    if not (source_dir / "SKILL.md").is_file():
        raise FileNotFoundError(f"Required SKILL.md not found in {source_dir}")

    output_dir.mkdir(parents=True, exist_ok=True)
    archive_path = output_dir / f"{skill_name}.zip"
    with ZipFile(archive_path, "w", compression=ZIP_DEFLATED) as archive:
        for item in sorted(source_dir.rglob("*")):
            if item.is_file():
                archive.write(item, item.relative_to(source_dir.parent))
    return archive_path


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo-root", type=Path, default=Path(__file__).resolve().parents[1])
    parser.add_argument("--output-dir", type=Path, default=None)
    args = parser.parse_args()

    root = args.repo_root.resolve()
    output_dir = (args.output_dir or root / "dist").resolve()
    skill_names = discover_skills(root)
    if not skill_names:
        raise SystemExit(f"No skills found under {root / 'skills'}")

    for skill_name in skill_names:
        print(f"Created: {package_skill(root, skill_name, output_dir)}")
    print(f"Packaged {len(skill_names)} HIF skills. See docs/INTEGRATIONS.md.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
