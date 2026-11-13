#!/usr/bin/env python3
"""Dependency-free structural checks for Remake skills and manifest."""
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
NAME_RE = re.compile(r"^[a-z][a-z0-9-]*$")

def validate(root=ROOT):
    errors = []
    manifest = root / ".claude-plugin" / "plugin.json"
    try:
        plugin = json.loads(manifest.read_text(encoding="utf-8"))
        if plugin.get("name") != "remake":
            errors.append("plugin name must be remake")
        if not plugin.get("version"):
            errors.append("plugin version is required")
    except (OSError, ValueError) as exc:
        errors.append(f"invalid plugin manifest: {exc}")

    skills = sorted((root / "skills").glob("*/SKILL.md"))
    if not skills:
        errors.append("no SKILL.md files found")
    names = set()
    for path in skills:
        content = path.read_text(encoding="utf-8")
        match = re.match(r"\A---\n(.*?)\n---\n", content, re.DOTALL)
        if not match:
            errors.append(f"{path.parent.name}: missing YAML frontmatter")
            continue
        front = match.group(1)
        values = dict(re.findall(r"^(name|description):\s*(.+)$", front, re.MULTILINE))
        name = values.get("name", "").strip()
        if not NAME_RE.fullmatch(name) or name != path.parent.name:
            errors.append(f"{path.parent.name}: invalid or mismatched name")
        if name in names:
            errors.append(f"{path.parent.name}: duplicate skill name")
        names.add(name)
        if len(values.get("description", "").strip()) < 30:
            errors.append(f"{path.parent.name}: description too short")
        if len(content.splitlines()) > 500:
            errors.append(f"{path.parent.name}: SKILL.md exceeds 500 lines")
    return errors

if __name__ == "__main__":
    issues = validate()
    if issues:
        for issue in issues:
            print("FAIL:", issue)
        raise SystemExit(1)
    print("PASS: plugin manifest and skill structure")
