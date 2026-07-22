#!/usr/bin/env python3
from __future__ import annotations

import json
import shutil
import subprocess
import sys
import tempfile
import urllib.error
import urllib.parse
import urllib.request
from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path

from observability_runtime import ScriptRun


ROOT = Path(__file__).resolve().parent.parent
REGISTRY_ROOT = ROOT / ".agentcodex" / "registry"
CACHE_ROOT = ROOT / ".agentcodex" / "cache"
REPORTS_ROOT = ROOT / ".agentcodex" / "reports"
SOURCES_PATH = REGISTRY_ROOT / "sources.yaml"
REPOS_LOCK_PATH = REGISTRY_ROOT / "repos-lock.yaml"
REPO_METADATA_ROOT = CACHE_ROOT / "repo-metadata"
SUMMARIES_ROOT = CACHE_ROOT / "summaries"
MANIFESTS_ROOT = CACHE_ROOT / "manifests"
REPORT_PATH = REPORTS_ROOT / "source-sync-report.md"
DEFAULT_CONTENT_PATHS = [
    "README.md",
    "README.rst",
    "README.txt",
    "docs",
    "examples",
    "example",
    "CHANGELOG.md",
    "CHANGES.md",
    "RELEASES.md",
    "docs/README.md",
]
SUMMARY_WORD_LIMIT = 120


@dataclass
class SourceEntry:
    source_id: str
    name: str
    repo: str
    category: str
    trust: str
    ingest_mode: str
    update_strategy: str


def print_usage() -> int:
    print(
        "Usage: python3 scripts/agentcodex.py sync-sources "
        "[--source <source-id>] [--apply] [--use-git] [--limit <n>] [--skip-lock-update]"
    )
    return 1


def load_sources() -> list[SourceEntry]:
    if not SOURCES_PATH.exists():
        raise SystemExit(f"Missing sources registry: {SOURCES_PATH}")

    version: str | None = None
    in_sources = False
    current: dict[str, str] | None = None
    items: list[dict[str, str]] = []

    for raw_line in SOURCES_PATH.read_text(encoding="utf-8").splitlines():
        line = raw_line.rstrip()
        stripped = line.strip()
        if not stripped or stripped.startswith("#"):
            continue
        if not line.startswith(" ") and stripped.startswith("version:"):
            version = stripped.split(":", 1)[1].strip()
            continue
        if not line.startswith(" ") and stripped == "sources:":
            in_sources = True
            current = None
            continue
        if not in_sources:
            continue
        if stripped.startswith("- "):
            if current:
                items.append(current)
            current = {}
            remainder = stripped[2:].strip()
            if remainder:
                key, value = remainder.split(":", 1)
                current[key.strip()] = value.strip()
            continue
        if current is None or ":" not in stripped:
            continue
        key, value = stripped.split(":", 1)
        current[key.strip()] = value.strip()

    if current:
        items.append(current)

    if version is None:
        raise SystemExit(f"Invalid sources registry missing version: {SOURCES_PATH}")

    entries: list[SourceEntry] = []
    required = {"id", "name", "repo", "category", "trust", "ingest_mode", "update_strategy"}
    for item in items:
        missing = sorted(required - set(item))
        if missing:
            raise SystemExit(
                f"Invalid source entry in {SOURCES_PATH}: missing {', '.join(missing)} for {item.get('id', '<unknown>')}"
            )
        entries.append(
            SourceEntry(
                source_id=item["id"],
                name=item["name"],
                repo=item["repo"],
                category=item["category"],
                trust=item["trust"],
                ingest_mode=item["ingest_mode"],
                update_strategy=item["update_strategy"],
            )
        )
    return entries


def github_repo_from_url(repo: str) -> tuple[str, str] | None:
    parsed = urllib.parse.urlparse(repo)
    if parsed.netloc not in {"github.com", "www.github.com"}:
        return None
    path = parsed.path.strip("/")
    parts = [part for part in path.split("/") if part]
    if len(parts) < 2:
        return None
    return parts[0], parts[1].removesuffix(".git")


def http_get_json(url: str) -> dict | list:
    request = urllib.request.Request(
        url,
        headers={
            "Accept": "application/vnd.github+json",
            "User-Agent": "AgentCodex/0.1.0",
        },
    )
    with urllib.request.urlopen(request, timeout=30) as response:
        return json.loads(response.read().decode("utf-8"))


def http_get_text(url: str) -> str:
    request = urllib.request.Request(
        url,
        headers={
            "Accept": "application/vnd.github.raw+json, application/vnd.github.raw",
            "User-Agent": "AgentCodex/0.1.0",
        },
    )
    with urllib.request.urlopen(request, timeout=30) as response:
        return response.read().decode("utf-8", errors="replace")


def summarize_text(text: str, limit: int = SUMMARY_WORD_LIMIT) -> str:
    words = text.replace("\r", " ").replace("\n", " ").split()
    if not words:
        return "No content captured."
    if len(words) <= limit:
        return " ".join(words)
    return " ".join(words[:limit]) + " ..."


def fetch_github_metadata(source: SourceEntry, use_git: bool) -> dict:
    repo_parts = github_repo_from_url(source.repo)
    if repo_parts is None:
        raise RuntimeError(f"Unsupported repo URL for source {source.source_id}: {source.repo}")

    owner, repo_name = repo_parts
    repo_api = f"https://api.github.com/repos/{owner}/{repo_name}"
    repo_data = http_get_json(repo_api)

    default_branch = repo_data.get("default_branch", "main")
    branch_data = http_get_json(f"{repo_api}/branches/{default_branch}")
    observed_ref = branch_data.get("commit", {}).get("sha", "")
    release_data: dict | None = None
    changelog_hits: list[dict[str, str]] = []
    content_hits: list[dict[str, str]] = []
    errors: list[str] = []

    try:
        release_payload = http_get_json(f"{repo_api}/releases/latest")
        if isinstance(release_payload, dict) and not release_payload.get("message"):
            release_data = {
                "name": release_payload.get("name") or release_payload.get("tag_name", ""),
                "tag_name": release_payload.get("tag_name", ""),
                "published_at": release_payload.get("published_at", ""),
                "html_url": release_payload.get("html_url", ""),
                "body_summary": summarize_text(release_payload.get("body", "")),
            }
    except urllib.error.HTTPError as exc:
        if exc.code != 404:
            errors.append(f"latest release lookup failed: HTTP {exc.code}")
    except Exception as exc:  # pragma: no cover - defensive
        errors.append(f"latest release lookup failed: {exc}")

    if use_git:
        git_snapshot = fetch_via_shallow_clone(source.repo, default_branch)
        content_hits = git_snapshot["content_hits"]
        changelog_hits = git_snapshot["changelog_hits"]
    else:
        tree_payload = http_get_json(f"{repo_api}/git/trees/{default_branch}?recursive=1")
        tree = tree_payload.get("tree", []) if isinstance(tree_payload, dict) else []
        available_paths = {
            item.get("path", ""): item.get("type", "")
            for item in tree
            if isinstance(item, dict) and item.get("path")
        }
        for candidate in DEFAULT_CONTENT_PATHS:
            object_type = available_paths.get(candidate)
            if object_type == "blob":
                try:
                    raw_url = f"https://raw.githubusercontent.com/{owner}/{repo_name}/{default_branch}/{candidate}"
                    text = http_get_text(raw_url)
                    entry = {
                        "path": candidate,
                        "summary": summarize_text(text),
                    }
                    content_hits.append(entry)
                    if candidate.upper().startswith("CHANGE") or "RELEASE" in candidate.upper():
                        changelog_hits.append(entry)
                except Exception as exc:  # pragma: no cover - defensive
                    errors.append(f"content fetch failed for {candidate}: {exc}")
            elif object_type == "tree":
                content_hits.append(
                    {
                        "path": candidate + "/",
                        "summary": "Directory detected. Content not expanded by default.",
                    }
                )

    metadata = {
        "source_id": source.source_id,
        "name": source.name,
        "repo": source.repo,
        "category": source.category,
        "trust": source.trust,
        "ingest_mode": source.ingest_mode,
        "update_strategy": source.update_strategy,
        "observed_at": datetime.now(UTC).isoformat(),
        "observed_ref": observed_ref,
        "default_branch": default_branch,
        "repo_metadata": {
            "description": repo_data.get("description", ""),
            "html_url": repo_data.get("html_url", ""),
            "topics": repo_data.get("topics", []),
            "stargazers_count": repo_data.get("stargazers_count", 0),
            "open_issues_count": repo_data.get("open_issues_count", 0),
            "license": (repo_data.get("license") or {}).get("spdx_id", ""),
            "updated_at": repo_data.get("updated_at", ""),
        },
        "release": release_data,
        "content_hits": content_hits,
        "changelog_hits": changelog_hits,
        "errors": errors,
    }
    return metadata


def fetch_via_shallow_clone(repo_url: str, branch: str) -> dict:
    with tempfile.TemporaryDirectory(prefix="agentcodex-source-sync-") as tmpdir:
        temp_root = Path(tmpdir)
        target_dir = temp_root / "repo"
        subprocess.run(
            [
                "git",
                "clone",
                "--depth",
                "1",
                "--branch",
                branch,
                "--filter=blob:none",
                "--sparse",
                repo_url,
                str(target_dir),
            ],
            check=True,
            cwd=str(temp_root),
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
        )
        subprocess.run(
            ["git", "sparse-checkout", "set", *DEFAULT_CONTENT_PATHS],
            check=True,
            cwd=str(target_dir),
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
        )
        content_hits: list[dict[str, str]] = []
        changelog_hits: list[dict[str, str]] = []
        for candidate in DEFAULT_CONTENT_PATHS:
            path = target_dir / candidate
            if path.is_file():
                entry = {
                    "path": candidate,
                    "summary": summarize_text(path.read_text(encoding="utf-8", errors="replace")),
                }
                content_hits.append(entry)
                if candidate.upper().startswith("CHANGE") or "RELEASE" in candidate.upper():
                    changelog_hits.append(entry)
            elif path.is_dir():
                content_hits.append(
                    {
                        "path": candidate + "/",
                        "summary": "Directory detected. Content not expanded by default.",
                    }
                )
        return {
            "content_hits": content_hits,
            "changelog_hits": changelog_hits,
        }


def write_json(path: Path, payload: dict | list) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=True) + "\n", encoding="utf-8")


def load_repos_lock() -> tuple[str, str, list[dict[str, str]]]:
    if not REPOS_LOCK_PATH.exists():
        return "0.1.0", "", []

    version = "0.1.0"
    description = ""
    entries: list[dict[str, str]] = []
    in_entries = False
    current: dict[str, str] | None = None
    for raw_line in REPOS_LOCK_PATH.read_text(encoding="utf-8").splitlines():
        line = raw_line.rstrip()
        stripped = line.strip()
        if not stripped or stripped.startswith("#"):
            continue
        if not line.startswith(" ") and stripped.startswith("version:"):
            version = stripped.split(":", 1)[1].strip()
            continue
        if not line.startswith(" ") and stripped.startswith("description:"):
            description = stripped.split(":", 1)[1].strip()
            continue
        if not line.startswith(" ") and stripped == "entries:":
            in_entries = True
            current = None
            continue
        if not in_entries:
            continue
        if stripped.startswith("- "):
            if current:
                entries.append(current)
            current = {}
            remainder = stripped[2:].strip()
            if remainder:
                key, value = remainder.split(":", 1)
                current[key.strip()] = value.strip()
            continue
        if current is not None and ":" in stripped:
            key, value = stripped.split(":", 1)
            current[key.strip()] = value.strip()
    if current:
        entries.append(current)
    return version, description, entries


def save_repos_lock(entries: list[dict[str, str]]) -> None:
    version, description, _ = load_repos_lock()
    lines = [
        f"version: {version}",
        f"description: {description or 'observed upstream repository state for trusted public sources used by AgentCodex'}",
        "entries:",
    ]
    if not entries:
        lines.append("  []")
    else:
        for entry in entries:
            lines.append(f"  - source_id: {entry['source_id']}")
            lines.append(f"    observed_ref: {entry['observed_ref']}")
            lines.append(f"    observed_at: {entry['observed_at']}")
            lines.append(f"    update_status: {entry['update_status']}")
            notes = entry["notes"].replace("\n", " ").strip() or "n/a"
            lines.append(f"    notes: {notes}")
    REPOS_LOCK_PATH.write_text("\n".join(lines) + "\n", encoding="utf-8")


def update_repos_lock(metadata_items: list[dict]) -> None:
    _, _, existing = load_repos_lock()
    by_id = {item["source_id"]: item for item in existing}
    for metadata in metadata_items:
        by_id[metadata["source_id"]] = {
            "source_id": metadata["source_id"],
            "observed_ref": metadata.get("observed_ref", ""),
            "observed_at": metadata.get("observed_at", ""),
            "update_status": "synced" if not metadata.get("errors") else "blocked",
            "notes": "; ".join(metadata.get("errors", [])) or "metadata captured",
        }
    save_repos_lock(sorted(by_id.values(), key=lambda item: item["source_id"]))


def write_report(results: list[dict], apply: bool, use_git: bool) -> None:
    REPORTS_ROOT.mkdir(parents=True, exist_ok=True)
    synced = len([item for item in results if not item.get("errors")])
    blocked = len(results) - synced
    coverage = round(synced / len(results), 4) if results else 0.0
    lines = [
        "# Source Sync Report",
        "",
        f"- generated_at: {datetime.now(UTC).isoformat()}",
        f"- mode: {'apply' if apply else 'dry-run'}",
        f"- transport: {'shallow-clone' if use_git else 'github-api'}",
        f"- source_count: {len(results)}",
        f"- synced_sources: {synced}",
        f"- blocked_sources: {blocked}",
        f"- source_inventory_coverage: {coverage}",
        "",
    ]
    for item in results:
        lines.extend(
            [
                f"## {item['source_id']}",
                "",
                f"- repo: {item['repo']}",
                f"- observed_ref: {item.get('observed_ref', '') or 'unknown'}",
                f"- status: {'blocked' if item.get('errors') else 'synced'}",
                f"- content_hits: {len(item.get('content_hits', []))}",
                f"- changelog_hits: {len(item.get('changelog_hits', []))}",
            ]
        )
        if item.get("errors"):
            lines.append(f"- errors: {'; '.join(item['errors'])}")
        lines.append("")
    REPORT_PATH.write_text("\n".join(lines), encoding="utf-8")


def main() -> int:
    run = ScriptRun(ROOT, "sync-sources")
    args = sys.argv[1:]
    selected_source: str | None = None
    apply = False
    use_git = False
    limit: int | None = None
    skip_lock_update = False

    i = 0
    while i < len(args):
        arg = args[i]
        if arg == "--source":
            if i + 1 >= len(args):
                return print_usage()
            selected_source = args[i + 1].strip()
            i += 2
            continue
        if arg == "--apply":
            apply = True
            i += 1
            continue
        if arg == "--use-git":
            use_git = True
            i += 1
            continue
        if arg == "--limit":
            if i + 1 >= len(args):
                return print_usage()
            limit = int(args[i + 1])
            i += 2
            continue
        if arg == "--skip-lock-update":
            skip_lock_update = True
            i += 1
            continue
        return print_usage()

    entries = load_sources()
    if selected_source:
        entries = [entry for entry in entries if entry.source_id == selected_source]
    if limit is not None:
        entries = entries[:limit]

    REPO_METADATA_ROOT.mkdir(parents=True, exist_ok=True)
    SUMMARIES_ROOT.mkdir(parents=True, exist_ok=True)
    MANIFESTS_ROOT.mkdir(parents=True, exist_ok=True)

    results: list[dict] = []
    for entry in entries:
        print(f"Syncing source metadata for {entry.source_id} from {entry.repo}")
        run.event("info", "syncing source metadata", source_id=entry.source_id, repo=entry.repo)
        try:
            metadata = fetch_github_metadata(entry, use_git=use_git)
        except Exception as exc:
            metadata = {
                "source_id": entry.source_id,
                "name": entry.name,
                "repo": entry.repo,
                "category": entry.category,
                "trust": entry.trust,
                "ingest_mode": entry.ingest_mode,
                "update_strategy": entry.update_strategy,
                "observed_at": datetime.now(UTC).isoformat(),
                "observed_ref": "",
                "content_hits": [],
                "changelog_hits": [],
                "errors": [str(exc)],
            }
            run.record_source_failure(entry.source_id, str(exc), "sync-sources")
            run.event("error", "source sync failed", source_id=entry.source_id, error=str(exc))
        results.append(metadata)

        if apply:
            write_json(REPO_METADATA_ROOT / f"{entry.source_id}.json", metadata)
            summary_payload = {
                "source_id": entry.source_id,
                "repo": entry.repo,
                "observed_ref": metadata.get("observed_ref", ""),
                "readme_summary": next(
                    (item["summary"] for item in metadata.get("content_hits", []) if item["path"].lower().startswith("readme")),
                    "No README summary captured.",
                ),
                "release_summary": (metadata.get("release") or {}).get("body_summary", ""),
            }
            write_json(SUMMARIES_ROOT / f"{entry.source_id}.json", summary_payload)

    manifest = {
        "generated_at": datetime.now(UTC).isoformat(),
        "apply": apply,
        "transport": "shallow-clone" if use_git else "github-api",
        "sources": [
            {
                "source_id": item["source_id"],
                "observed_ref": item.get("observed_ref", ""),
                "status": "blocked" if item.get("errors") else "synced",
            }
            for item in results
        ],
    }
    if apply:
        write_json(MANIFESTS_ROOT / "source-sync-manifest.json", manifest)
        if not skip_lock_update:
            update_repos_lock(results)
    write_report(results, apply=apply, use_git=use_git)
    successful = len([item for item in results if not item.get("errors")])
    failures = len(results) - successful
    coverage = round(successful / len(results), 4) if results else 0.0
    freshness = datetime.now(UTC).isoformat()
    run.metric("sources_checked", len(results))
    run.metric("sources_synced", successful)
    run.metric("sources_failed", failures)
    run.metric("coverage", coverage)
    run.metric("source_inventory_coverage", coverage)
    run.metric("freshness", freshness)
    run.metric("update_success_rate", coverage)
    run.finalize(
        "success",
        {
            "apply": apply,
            "transport": manifest["transport"],
            "results": len(results),
        },
    )

    print(
        f"{'Applied' if apply else 'Dry run'} source sync for "
        f"{len(results)} source(s). Report: {REPORT_PATH.relative_to(ROOT)}"
    )
    if not apply:
        print("Use --apply to write metadata into .agentcodex/cache and update repos-lock.yaml.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
