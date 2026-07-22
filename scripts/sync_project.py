#!/usr/bin/env python3
from __future__ import annotations

import hashlib
import shutil
import sys
from pathlib import Path

from kb_domains import KB_DOMAIN_PATHS, KB_MANAGED_DOMAINS


ROOT = Path(__file__).resolve().parent.parent
BOOTSTRAP_ROOT = ROOT / ".agentcodex" / "bootstrap"
PROJECT_TEMPLATE = BOOTSTRAP_ROOT / "PROJECT_AGENTSCODEX_TEMPLATE.md"
EXAMPLE_DEFINE_TEMPLATE = BOOTSTRAP_ROOT / "EXAMPLE_DEFINE_TEMPLATE.md"
ROUTING_SOURCE = ROOT / ".agentcodex" / "routing" / "routing.json"
KB_SOURCE = ROOT / ".agentcodex" / "kb"
TEMPLATES_SOURCE = ROOT / ".agentcodex" / "templates"
COMMANDS_SOURCE = ROOT / "docs" / "commands"
CODEX_SOURCE = BOOTSTRAP_ROOT / "codex"
PROJECT_STANDARD_SOURCE = BOOTSTRAP_ROOT / "PROJECT_STANDARD_FEATURE"
PROJECT_STANDARD_MANIFEST = ROOT / ".agentcodex" / "project-standard.json"
MATURITY_SOURCE = ROOT / ".agentcodex" / "maturity"
MATURITY_PROFILE_OVERLAYS = ROOT / ".agentcodex" / "bootstrap" / "MATURITY_PROFILE_OVERLAYS"


def resolve_profile(args: list[str]) -> tuple[Path, bool, str | None, str] | None:
    with_codex = False
    profile: str | None = None
    sync_mode = "light"
    positional: list[str] = []
    i = 0
    while i < len(args):
        arg = args[i]
        if arg == "--with-codex":
            with_codex = True
            i += 1
            continue
        if arg == "--full":
            sync_mode = "full"
            i += 1
            continue
        if arg == "--light":
            sync_mode = "light"
            i += 1
            continue
        if arg == "--mode":
            if i + 1 >= len(args):
                return None
            sync_mode = args[i + 1]
            i += 2
            continue
        if arg == "--profile":
            if i + 1 >= len(args):
                return None
            profile = args[i + 1]
            sync_mode = "full"
            i += 2
            continue
        positional.append(arg)
        i += 1
    if len(positional) != 1 or sync_mode not in {"light", "full"}:
        return None
    return Path(positional[0]).resolve(), with_codex, profile, sync_mode


def active_profile(target: Path, override: str | None) -> str | None:
    if override:
        return override
    marker = target / ".agentcodex" / "maturity" / "ACTIVE_PROFILE.md"
    if not marker.exists():
        return None
    for line in marker.read_text(encoding="utf-8").splitlines():
        if line.startswith("- profile_id:"):
            return line.split("`", 2)[1]
    return None


def sync_profile_overlay(target: Path, drift: dict[str, list[str]], profile: str) -> None:
    overlay_root = MATURITY_PROFILE_OVERLAYS / profile
    if not overlay_root.exists():
        raise ValueError(profile)
    active_profile_dest = target / ".agentcodex" / "maturity" / "ACTIVE_PROFILE.md"
    record_drift(drift, "maturity", active_profile_dest, classify_file_state(overlay_root / "PROFILE.md", active_profile_dest))
    copy_file(overlay_root / "PROFILE.md", active_profile_dest)
    ops_root = overlay_root / "ops"
    sync_tree(
        ops_root,
        target / ".agentcodex" / "ops",
        [path.name for path in ops_root.iterdir() if path.is_dir()],
        drift,
        "maturity",
    )


def file_digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def copy_file(src: Path, dest: Path) -> None:
    if src.resolve() == dest.resolve():
        return
    dest.parent.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(src, dest)


def classify_file_state(src: Path, dest: Path) -> str:
    if not dest.exists():
        return "missing"
    if file_digest(src) != file_digest(dest):
        return "outdated"
    return "current"


def record_drift(drift: dict[str, list[str]], category: str, dest: Path, state: str) -> None:
    if state == "current":
        return
    drift.setdefault(category, []).append(f"{state}: {dest}")


def record_extra_files(
    drift: dict[str, list[str]],
    category: str,
    source_dir: Path,
    target_dir: Path,
    pattern: str = "*",
) -> None:
    if not target_dir.exists():
        return
    expected = {
        path.name
        for path in source_dir.glob(pattern)
        if path.is_file()
    }
    for path in sorted(target_dir.glob(pattern)):
        if path.is_file() and path.name not in expected:
            record_drift(drift, category, path, "extra")


def sync_dir(
    source_dir: Path,
    target_dir: Path,
    drift: dict[str, list[str]],
    category: str,
    pattern: str = "*",
) -> None:
    if source_dir.resolve() == target_dir.resolve():
        return
    target_dir.mkdir(parents=True, exist_ok=True)
    for item in source_dir.glob(pattern):
        if item.is_file():
            dest = target_dir / item.name
            record_drift(drift, category, dest, classify_file_state(item, dest))
            copy_file(item, dest)
    record_extra_files(drift, category, source_dir, target_dir, pattern)


def sync_tree(source_dir: Path, target_dir: Path, subdirs: list[str], drift: dict[str, list[str]], category: str) -> None:
    if source_dir.resolve() == target_dir.resolve():
        return
    target_dir.mkdir(parents=True, exist_ok=True)
    expected_dirs = {name.split("/", 1)[0] for name in subdirs}
    for path in sorted(target_dir.iterdir()):
        if path.is_dir() and path.name not in expected_dirs:
            record_drift(drift, category, path, "extra")
    for name in subdirs:
        src = source_dir / name
        dest = target_dir / name
        if not dest.exists():
            record_drift(drift, category, dest, "missing")
        else:
            src_files = {
                path.relative_to(src): file_digest(path)
                for path in src.rglob("*")
                if path.is_file()
            }
            dest_files = {
                path.relative_to(dest): file_digest(path)
                for path in dest.rglob("*")
                if path.is_file()
            }
            if src_files != dest_files:
                record_drift(drift, category, dest, "outdated")
        dest.mkdir(parents=True, exist_ok=True)
        for path in sorted(src.rglob("*")):
            rel = path.relative_to(src)
            target = dest / rel
            if path.is_dir():
                target.mkdir(parents=True, exist_ok=True)
                continue
            copy_file(path, target)


def main() -> int:
    if not sys.argv[1:] or sys.argv[1] in {"help", "--help", "-h"}:
        print(
            "Usage: python3 scripts/sync_project.py <target-project-dir> "
            "[--mode light|full] [--full] [--with-codex] [--profile <profile-id>]"
        )
        return 0

    resolved = resolve_profile(sys.argv[1:])
    if resolved is None:
        print(
            "Usage: python3 scripts/sync_project.py <target-project-dir> "
            "[--mode light|full] [--full] [--with-codex] [--profile <profile-id>]"
        )
        return 1

    target, with_codex, profile_override, sync_mode = resolved
    self_target = target.resolve() == ROOT.resolve()

    if not target.exists():
        print(f"Target does not exist: {target}")
        return 1

    drift: dict[str, list[str]] = {}
    managed_root = target / ".agentcodex"
    managed_root.mkdir(parents=True, exist_ok=True)

    for relative in [
        "features",
        "reports",
        "archive",
        "history",
    ]:
        (managed_root / relative).mkdir(parents=True, exist_ok=True)

    project_note = managed_root / "PROJECT_AGENTSCODEX.md"
    record_drift(drift, "bootstrap", project_note, classify_file_state(PROJECT_TEMPLATE, project_note))
    copy_file(PROJECT_TEMPLATE, project_note)

    if sync_mode == "light":
        print(f"Synchronized lightweight AgentCodex project state in {target}")
        print(f"Updated: {managed_root / 'PROJECT_AGENTSCODEX.md'}")
        print(f"Ensured: {managed_root / 'features'}")
        print(f"Ensured: {managed_root / 'reports'}")
        print(f"Ensured: {managed_root / 'archive'}")
        print(f"Ensured: {managed_root / 'history'}")
        print("Runtime assets remain in the AgentCodex plugin/package. Use --full to vendor them into the project.")
        if drift:
            print("Drift summary before sync:")
            for category in sorted(drift):
                missing = sum(1 for item in drift[category] if item.startswith("missing:"))
                outdated = sum(1 for item in drift[category] if item.startswith("outdated:"))
                extra = sum(1 for item in drift[category] if item.startswith("extra:"))
                print(f"- {category}: {missing} missing, {outdated} outdated, {extra} extra")
                for item in sorted(drift[category]):
                    print(f"  {item}")
        else:
            print("No managed drift detected.")
        return 0

    for relative in [
        "templates",
        "commands",
        "kb",
        "routing",
        "maturity",
        "ops",
    ]:
        (managed_root / relative).mkdir(parents=True, exist_ok=True)

    example_define_dest = managed_root / "features" / "DEFINE_EXAMPLE_PROJECT_FEATURE.md"
    if not example_define_dest.exists():
        record_drift(drift, "bootstrap", example_define_dest, "missing")
        copy_file(EXAMPLE_DEFINE_TEMPLATE, example_define_dest)
    project_standard_dest = managed_root / "features" / "example-project-standard"
    if not project_standard_dest.exists():
        record_drift(drift, "bootstrap", project_standard_dest, "missing")
    else:
        src_files = {
            path.relative_to(PROJECT_STANDARD_SOURCE): file_digest(path)
            for path in PROJECT_STANDARD_SOURCE.rglob("*")
            if path.is_file()
        }
        dest_files = {
            path.relative_to(project_standard_dest): file_digest(path)
            for path in project_standard_dest.rglob("*")
            if path.is_file()
        }
        if src_files != dest_files:
            record_drift(drift, "bootstrap", project_standard_dest, "outdated")
    project_standard_dest.mkdir(parents=True, exist_ok=True)
    for path in sorted(PROJECT_STANDARD_SOURCE.rglob("*")):
        rel = path.relative_to(PROJECT_STANDARD_SOURCE)
        target = project_standard_dest / rel
        if path.is_dir():
            target.mkdir(parents=True, exist_ok=True)
            continue
        copy_file(path, target)
    project_standard_manifest_dest = managed_root / "project-standard.json"
    record_drift(
        drift,
        "bootstrap",
        project_standard_manifest_dest,
        classify_file_state(PROJECT_STANDARD_MANIFEST, project_standard_manifest_dest),
    )
    copy_file(PROJECT_STANDARD_MANIFEST, project_standard_manifest_dest)
    sync_dir(MATURITY_SOURCE, managed_root / "maturity", drift, "maturity", "*.json")
    profile = active_profile(target, profile_override)
    if profile:
        try:
            sync_profile_overlay(target, drift, profile)
        except ValueError:
            print(f"Unknown maturity profile: {profile}")
            available = ", ".join(sorted(path.name for path in MATURITY_PROFILE_OVERLAYS.iterdir() if path.is_dir()))
            print(f"Available profiles: {available}")
            return 1

    sync_dir(TEMPLATES_SOURCE, managed_root / "templates", drift, "templates", "*.md")
    sync_dir(COMMANDS_SOURCE, managed_root / "commands", drift, "commands", "*.md")
    routing_dest = managed_root / "routing" / "routing.json"
    record_drift(drift, "routing", routing_dest, classify_file_state(ROUTING_SOURCE, routing_dest))
    copy_file(ROUTING_SOURCE, routing_dest)
    kb_readme_dest = managed_root / "kb" / "README.md"
    kb_index_dest = managed_root / "kb" / "index.yaml"
    record_drift(drift, "kb", kb_readme_dest, classify_file_state(KB_SOURCE / "README.md", kb_readme_dest))
    record_drift(drift, "kb", kb_index_dest, classify_file_state(KB_SOURCE / "index.yaml", kb_index_dest))
    copy_file(KB_SOURCE / "README.md", kb_readme_dest)
    copy_file(KB_SOURCE / "index.yaml", kb_index_dest)

    sync_tree(
        KB_SOURCE,
        managed_root / "kb",
        [KB_DOMAIN_PATHS[name] for name in KB_MANAGED_DOMAINS],
        drift,
        "kb",
    )

    if not self_target and (with_codex or (target / ".codex").exists()):
        codex_dir = target / ".codex"
        agents_dir = codex_dir / "agents"
        agents_dir.mkdir(parents=True, exist_ok=True)
        codex_config_dest = codex_dir / "config.toml"
        record_drift(
            drift,
            "codex",
            codex_config_dest,
            classify_file_state(CODEX_SOURCE / "config.toml", codex_config_dest),
        )
        copy_file(CODEX_SOURCE / "config.toml", codex_config_dest)
        for agent_file in (CODEX_SOURCE / "agents").glob("*.toml"):
            dest = agents_dir / agent_file.name
            record_drift(drift, "codex", dest, classify_file_state(agent_file, dest))
            copy_file(agent_file, dest)
        record_extra_files(drift, "codex", CODEX_SOURCE / "agents", agents_dir, "*.toml")

    print(f"Synchronized AgentCodex-managed files in {target}")
    print(f"Updated: {managed_root / 'PROJECT_AGENTSCODEX.md'}")
    print(f"Updated: {managed_root / 'project-standard.json'}")
    print(f"Updated: {managed_root / 'maturity'}")
    if profile:
        print(f"Updated: {managed_root / 'ops'}")
        print(f"Active maturity profile: {profile}")
    print(f"Updated: {managed_root / 'templates'}")
    print(f"Updated: {managed_root / 'commands'}")
    print(f"Updated: {managed_root / 'routing' / 'routing.json'}")
    print(f"Updated: {managed_root / 'kb'}")
    if self_target:
        print("Skipped .codex sync for repository source target.")
    if drift:
        print("Drift summary before sync:")
        for category in sorted(drift):
            missing = sum(1 for item in drift[category] if item.startswith("missing:"))
            outdated = sum(1 for item in drift[category] if item.startswith("outdated:"))
            extra = sum(1 for item in drift[category] if item.startswith("extra:"))
            print(f"- {category}: {missing} missing, {outdated} outdated, {extra} extra")
            for item in sorted(drift[category]):
                print(f"  {item}")
    else:
        print("Drift summary before sync:")
        print("- no managed drift detected")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
