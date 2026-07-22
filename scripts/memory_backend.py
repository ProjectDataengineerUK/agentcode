#!/usr/bin/env python3
from __future__ import annotations

import json
import os
import urllib.error
import urllib.request
from dataclasses import dataclass
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
MEMORY_ROOT = ROOT / ".agentcodex" / "memory"
CACHE_ROOT = ROOT / ".agentcodex" / "cache" / "memory"
SUMMARY_PATH = CACHE_ROOT / "summaries" / "local-memory-summary.md"
DEFAULT_SNAPSHOT_PATHS = {
    "semantic": CACHE_ROOT / "snapshots" / "semantic-memories.json",
    "episodic": CACHE_ROOT / "snapshots" / "episodic-memories.json",
    "procedural": CACHE_ROOT / "snapshots" / "procedural-memories.json",
}


def parse_simple_yaml(path: Path) -> dict:
    data: dict = {}
    current_list_key: str | None = None
    current_item: dict | None = None
    for raw_line in path.read_text(encoding="utf-8").splitlines():
        line = raw_line.rstrip()
        stripped = line.strip()
        if not stripped or stripped.startswith("#"):
            continue
        if not line.startswith(" ") and ":" in stripped:
            key, value = stripped.split(":", 1)
            key = key.strip()
            value = value.strip()
            current_list_key = None
            current_item = None
            if value == "":
                data[key] = []
                current_list_key = key
            elif value == "[]":
                data[key] = []
            else:
                data[key] = value
            continue
        if current_list_key and stripped.startswith("- "):
            if ":" in stripped[2:]:
                key, value = stripped[2:].split(":", 1)
                current_item = {key.strip(): value.strip()}
                data[current_list_key].append(current_item)
            else:
                data[current_list_key].append(stripped[2:].strip())
            continue
        if current_item is not None and ":" in stripped:
            key, value = stripped.split(":", 1)
            current_item[key.strip()] = value.strip()
    return data


@dataclass(frozen=True)
class MemoryHealth:
    backend_id: str
    status: str
    active_sources: int
    writable: bool


class MemoryBackend:
    backend_id: str

    def snapshot_paths(self) -> dict[str, Path]:
        raise NotImplementedError

    def summary_path(self) -> Path:
        raise NotImplementedError

    def load(self, memory_type: str) -> list[dict]:
        raise NotImplementedError

    def upsert(self, memory_type: str, items: list[dict]) -> None:
        raise NotImplementedError

    def compact(self, compacted: dict[str, list[dict]], summary_text: str, index_payload: dict) -> None:
        raise NotImplementedError

    def health(self) -> MemoryHealth:
        raise NotImplementedError


class LocalMockMemoryBackend(MemoryBackend):
    def __init__(self) -> None:
        self.backend_id = "local-mock"
        self._sources = active_sources_for_backend(self.backend_id)

    def snapshot_paths(self) -> dict[str, Path]:
        resolved = dict(DEFAULT_SNAPSHOT_PATHS)
        for memory_type, config in self._sources.items():
            path_value = config.get("path")
            if path_value and memory_type in resolved:
                resolved[memory_type] = ROOT / str(path_value)
        return resolved

    def summary_path(self) -> Path:
        summary_config = self._sources.get("summary", {})
        path_value = summary_config.get("path")
        if path_value:
            return ROOT / str(path_value)
        return SUMMARY_PATH

    def load(self, memory_type: str) -> list[dict]:
        path = self.snapshot_paths()[memory_type]
        if not path.exists():
            return []
        return json.loads(path.read_text(encoding="utf-8"))

    def upsert(self, memory_type: str, items: list[dict]) -> None:
        path = self.snapshot_paths()[memory_type]
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(items, indent=2) + "\n", encoding="utf-8")

    def compact(self, compacted: dict[str, list[dict]], summary_text: str, index_payload: dict) -> None:
        for memory_type, items in compacted.items():
            self.upsert(memory_type, items)
        summary_path = self.summary_path()
        summary_path.parent.mkdir(parents=True, exist_ok=True)
        summary_path.write_text(summary_text, encoding="utf-8")
        index_path = CACHE_ROOT / "indexes" / "memory-index.json"
        index_path.parent.mkdir(parents=True, exist_ok=True)
        index_path.write_text(json.dumps(index_payload, indent=2) + "\n", encoding="utf-8")

    def health(self) -> MemoryHealth:
        paths = self.snapshot_paths()
        writable = all(path.parent.exists() or path.parent == path.parent for path in paths.values())
        return MemoryHealth(
            backend_id=self.backend_id,
            status="active",
            active_sources=len(self._sources),
            writable=writable,
        )


class QdrantMemoryBackend(MemoryBackend):
    vector_size = 32

    def __init__(self) -> None:
        self.backend_id = "qdrant"
        self.base_url = os.environ.get("AGENTCODEX_MEMORY_QDRANT_URL", "").rstrip("/")
        self.api_key = os.environ.get("AGENTCODEX_MEMORY_QDRANT_API_KEY", "")
        self.collection_prefix = os.environ.get("AGENTCODEX_MEMORY_QDRANT_COLLECTION_PREFIX", "agentcodex-memory")
        self.local_fallback = LocalMockMemoryBackend()

    def snapshot_paths(self) -> dict[str, Path]:
        return self.local_fallback.snapshot_paths()

    def summary_path(self) -> Path:
        return self.local_fallback.summary_path()

    def load(self, memory_type: str) -> list[dict]:
        payloads = self._scroll_payloads(memory_type)
        return [payload for payload in payloads if isinstance(payload, dict)]

    def upsert(self, memory_type: str, items: list[dict]) -> None:
        self._ensure_configured()
        self._ensure_collection(memory_type)
        points = []
        for item in items:
            points.append(
                {
                    "id": str(item.get("memory_id")),
                    "vector": self.vectorize_payload(item, memory_type),
                    "payload": item,
                }
            )
        self._request(
            "PUT",
            f"/collections/{self.collection_name(memory_type)}/points?wait=true",
            {"points": points},
        )

    def compact(self, compacted: dict[str, list[dict]], summary_text: str, index_payload: dict) -> None:
        for memory_type, items in compacted.items():
            self.upsert(memory_type, items)
        summary_path = self.summary_path()
        summary_path.parent.mkdir(parents=True, exist_ok=True)
        summary_path.write_text(summary_text, encoding="utf-8")
        index_path = CACHE_ROOT / "indexes" / "memory-index.json"
        index_path.parent.mkdir(parents=True, exist_ok=True)
        payload = dict(index_payload)
        payload["backend"] = self.backend_id
        index_path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")

    def health(self) -> MemoryHealth:
        if not self.base_url:
            return MemoryHealth(
                backend_id=self.backend_id,
                status="configured-missing-url",
                active_sources=0,
                writable=False,
            )
        try:
            response = self._request("GET", "/collections")
            result = response.get("result", {}).get("collections", [])
            return MemoryHealth(
                backend_id=self.backend_id,
                status="active",
                active_sources=len(result) if isinstance(result, list) else 0,
                writable=True,
            )
        except RuntimeError:
            return MemoryHealth(
                backend_id=self.backend_id,
                status="unreachable",
                active_sources=0,
                writable=False,
            )

    def collection_name(self, memory_type: str) -> str:
        return f"{self.collection_prefix}-{memory_type}"

    def vectorize_payload(self, item: dict, memory_type: str) -> list[float]:
        text = self.payload_text(item, memory_type)
        buckets = [0.0] * self.vector_size
        for token in text.casefold().split():
            slot = sum(ord(char) for char in token) % self.vector_size
            buckets[slot] += 1.0
        norm = sum(value * value for value in buckets) ** 0.5
        if norm == 0.0:
            return buckets
        return [round(value / norm, 6) for value in buckets]

    def payload_text(self, item: dict, memory_type: str) -> str:
        if memory_type == "semantic":
            return " ".join(
                str(item.get(key, ""))
                for key in ["subject", "canonical_fact", "supporting_context"]
            )
        if memory_type == "episodic":
            return " ".join(
                str(item.get(key, ""))
                for key in ["event_title", "event_summary", "outcome"]
            )
        return " ".join(
            str(item.get(key, ""))
            for key in ["procedure_title", "trigger", "approval_state"]
        )

    def _scroll_payloads(self, memory_type: str) -> list[dict]:
        self._ensure_configured()
        self._ensure_collection(memory_type)
        points: list[dict] = []
        offset = None
        while True:
            body = {"limit": 128, "with_payload": True, "with_vector": False}
            if offset is not None:
                body["offset"] = offset
            response = self._request(
                "POST",
                f"/collections/{self.collection_name(memory_type)}/points/scroll",
                body,
            )
            result = response.get("result", {})
            batch = result.get("points", [])
            points.extend(item.get("payload", {}) for item in batch if isinstance(item, dict))
            offset = result.get("next_page_offset")
            if not offset:
                break
        return points

    def _ensure_collection(self, memory_type: str) -> None:
        try:
            self._request("GET", f"/collections/{self.collection_name(memory_type)}")
        except RuntimeError:
            self._request(
                "PUT",
                f"/collections/{self.collection_name(memory_type)}",
                {
                    "vectors": {
                        "size": self.vector_size,
                        "distance": "Cosine",
                    }
                },
            )

    def _ensure_configured(self) -> None:
        if not self.base_url:
            raise RuntimeError("qdrant backend requires AGENTCODEX_MEMORY_QDRANT_URL")

    def _request(self, method: str, path: str, payload: dict | None = None) -> dict:
        self._ensure_configured()
        data = None
        headers = {"Content-Type": "application/json"}
        if self.api_key:
            headers["api-key"] = self.api_key
        if payload is not None:
            data = json.dumps(payload).encode("utf-8")
        request = urllib.request.Request(
            f"{self.base_url}{path}",
            data=data,
            headers=headers,
            method=method,
        )
        try:
            with urllib.request.urlopen(request, timeout=10) as response:
                content = response.read().decode("utf-8")
        except urllib.error.HTTPError as exc:
            if exc.code == 404:
                raise RuntimeError("not-found") from exc
            raise RuntimeError(f"qdrant request failed: {exc.code}") from exc
        except urllib.error.URLError as exc:
            raise RuntimeError(f"qdrant request failed: {exc.reason}") from exc
        return json.loads(content) if content else {}


class Mem0MemoryBackend(MemoryBackend):
    def __init__(self) -> None:
        self.backend_id = "mem0"
        self.base_url = os.environ.get("AGENTCODEX_MEMORY_MEM0_URL", "").rstrip("/")
        self.api_key = os.environ.get("AGENTCODEX_MEMORY_MEM0_API_KEY", "")
        self.project_id = os.environ.get("AGENTCODEX_MEMORY_MEM0_PROJECT", "")
        self.local_fallback = LocalMockMemoryBackend()

    def snapshot_paths(self) -> dict[str, Path]:
        return self.local_fallback.snapshot_paths()

    def summary_path(self) -> Path:
        return self.local_fallback.summary_path()

    def load(self, memory_type: str) -> list[dict]:
        response = self._request("GET", f"/v1/memories?memory_type={memory_type}")
        return self._extract_memories(response)

    def upsert(self, memory_type: str, items: list[dict]) -> None:
        payload = {
            "memory_type": memory_type,
            "memories": items,
        }
        self._request("POST", "/v1/memories/batch", payload)

    def compact(self, compacted: dict[str, list[dict]], summary_text: str, index_payload: dict) -> None:
        for memory_type, items in compacted.items():
            self.upsert(memory_type, items)
        summary_path = self.summary_path()
        summary_path.parent.mkdir(parents=True, exist_ok=True)
        summary_path.write_text(summary_text, encoding="utf-8")
        index_path = CACHE_ROOT / "indexes" / "memory-index.json"
        index_path.parent.mkdir(parents=True, exist_ok=True)
        payload = dict(index_payload)
        payload["backend"] = self.backend_id
        index_path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")

    def health(self) -> MemoryHealth:
        if not self.base_url:
            return MemoryHealth(
                backend_id=self.backend_id,
                status="configured-missing-url",
                active_sources=0,
                writable=False,
            )
        if not self.api_key:
            return MemoryHealth(
                backend_id=self.backend_id,
                status="configured-missing-api-key",
                active_sources=0,
                writable=False,
            )
        try:
            response = self._request("GET", "/v1/memories?limit=1")
            memories = self._extract_memories(response)
            return MemoryHealth(
                backend_id=self.backend_id,
                status="active",
                active_sources=len(memories),
                writable=True,
            )
        except RuntimeError:
            return MemoryHealth(
                backend_id=self.backend_id,
                status="unreachable",
                active_sources=0,
                writable=False,
            )

    def _extract_memories(self, response: dict | list) -> list[dict]:
        if isinstance(response, list):
            return [item for item in response if isinstance(item, dict)]
        if not isinstance(response, dict):
            return []
        for key in ("memories", "results", "data"):
            value = response.get(key)
            if isinstance(value, list):
                return [item for item in value if isinstance(item, dict)]
        nested = response.get("result")
        if isinstance(nested, dict):
            for key in ("memories", "results", "data"):
                value = nested.get(key)
                if isinstance(value, list):
                    return [item for item in value if isinstance(item, dict)]
        return []

    def _request(self, method: str, path: str, payload: dict | None = None) -> dict | list:
        self._ensure_configured()
        data = None
        headers = {"Content-Type": "application/json", "Authorization": f"Bearer {self.api_key}"}
        if self.project_id:
            headers["X-Project-Id"] = self.project_id
        if payload is not None:
            data = json.dumps(payload).encode("utf-8")
        request = urllib.request.Request(
            f"{self.base_url}{path}",
            data=data,
            headers=headers,
            method=method,
        )
        try:
            with urllib.request.urlopen(request, timeout=10) as response:
                content = response.read().decode("utf-8")
        except urllib.error.HTTPError as exc:
            raise RuntimeError(f"mem0 request failed: {exc.code}") from exc
        except urllib.error.URLError as exc:
            raise RuntimeError(f"mem0 request failed: {exc.reason}") from exc
        return json.loads(content) if content else {}

    def _ensure_configured(self) -> None:
        if not self.base_url:
            raise RuntimeError("mem0 backend requires AGENTCODEX_MEMORY_MEM0_URL")
        if not self.api_key:
            raise RuntimeError("mem0 backend requires AGENTCODEX_MEMORY_MEM0_API_KEY")


class StubMemoryBackend(MemoryBackend):
    def __init__(self, backend_id: str) -> None:
        self.backend_id = backend_id

    def snapshot_paths(self) -> dict[str, Path]:
        return dict(DEFAULT_SNAPSHOT_PATHS)

    def summary_path(self) -> Path:
        return SUMMARY_PATH

    def load(self, memory_type: str) -> list[dict]:
        raise NotImplementedError(f"{self.backend_id} backend is not implemented yet")

    def upsert(self, memory_type: str, items: list[dict]) -> None:
        raise NotImplementedError(f"{self.backend_id} backend is not implemented yet")

    def compact(self, compacted: dict[str, list[dict]], summary_text: str, index_payload: dict) -> None:
        raise NotImplementedError(f"{self.backend_id} backend is not implemented yet")

    def health(self) -> MemoryHealth:
        return MemoryHealth(
            backend_id=self.backend_id,
            status="planned",
            active_sources=0,
            writable=False,
        )


def load_backend_manifest() -> dict:
    return parse_simple_yaml(MEMORY_ROOT / "manifests" / "memory-backends.yaml")


def active_backend_id() -> str:
    manifest = load_backend_manifest()
    return str(manifest.get("default_backend", "auto"))


def qdrant_backend_is_configured() -> bool:
    return bool(os.environ.get("AGENTCODEX_MEMORY_QDRANT_URL", "").strip())


def resolve_auto_backend() -> MemoryBackend:
    if qdrant_backend_is_configured():
        return QdrantMemoryBackend()
    return LocalMockMemoryBackend()


def active_sources_for_backend(backend_id: str) -> dict[str, dict]:
    manifest = parse_simple_yaml(MEMORY_ROOT / "manifests" / "memory-sources.yaml")
    resolved: dict[str, dict] = {}
    for item in manifest.get("sources", []):
        if not isinstance(item, dict):
            continue
        if item.get("status") != "active":
            continue
        if item.get("backend") != backend_id:
            continue
        memory_type = item.get("memory_type")
        if memory_type:
            resolved[str(memory_type)] = item
    return resolved


def get_backend(backend_id: str | None = None) -> MemoryBackend:
    resolved = backend_id or active_backend_id()
    if resolved == "auto":
        return resolve_auto_backend()
    if resolved == "local-mock":
        return LocalMockMemoryBackend()
    if resolved == "mem0":
        return Mem0MemoryBackend()
    if resolved == "qdrant":
        return QdrantMemoryBackend()
    if resolved in {"langmem"}:
        return StubMemoryBackend(resolved)
    raise ValueError(f"unsupported memory backend: {resolved}")
