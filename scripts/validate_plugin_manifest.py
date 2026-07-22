#!/usr/bin/env python3
from __future__ import annotations

import json
import re
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
PLUGIN_MANIFEST_PATH = ROOT / "plugins" / "agentcodex" / ".codex-plugin" / "plugin.json"
RE_VERSION = re.compile(r"^\d+\.\d+\.\d+$")
RE_HTTPS_URL = re.compile(r"^https://[^\s]+$")
RE_EMAIL = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")


def main() -> int:
    if not PLUGIN_MANIFEST_PATH.exists():
        print(f"Missing plugin manifest: {PLUGIN_MANIFEST_PATH}", file=sys.stderr)
        return 1

    try:
        payload = json.loads(PLUGIN_MANIFEST_PATH.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        print(f"Invalid JSON in plugin manifest: {exc}", file=sys.stderr)
        return 1

    errors: list[str] = []

    for key in ("name", "version", "description", "homepage", "repository", "license", "skills"):
        value = payload.get(key)
        if not isinstance(value, str) or not value.strip():
            errors.append(f"Missing non-empty string field: {key}")

    if isinstance(payload.get("version"), str) and not RE_VERSION.match(payload["version"]):
        errors.append(f"Invalid semantic version: {payload['version']}")

    for key in ("homepage", "repository"):
        value = payload.get(key, "")
        if isinstance(value, str) and value and not RE_HTTPS_URL.match(value):
            errors.append(f"Invalid HTTPS URL in {key}: {value}")

    author = payload.get("author")
    if not isinstance(author, dict):
        errors.append("Missing author object")
    else:
        for key in ("name", "email", "url"):
            value = author.get(key)
            if not isinstance(value, str) or not value.strip():
                errors.append(f"Missing author.{key}")
        email = author.get("email", "")
        if isinstance(email, str) and email:
            if "[TODO:" in email or not RE_EMAIL.match(email):
                errors.append(f"Invalid author.email: {email}")
        url = author.get("url", "")
        if isinstance(url, str) and url and not RE_HTTPS_URL.match(url):
            errors.append(f"Invalid author.url: {url}")

    interface = payload.get("interface")
    if not isinstance(interface, dict):
        errors.append("Missing interface object")
    else:
        required_strings = (
            "displayName",
            "shortDescription",
            "longDescription",
            "developerName",
            "category",
            "websiteURL",
            "privacyPolicyURL",
            "termsOfServiceURL",
            "brandColor",
        )
        for key in required_strings:
            value = interface.get(key)
            if not isinstance(value, str) or not value.strip():
                errors.append(f"Missing interface.{key}")
        for key in ("websiteURL", "privacyPolicyURL", "termsOfServiceURL"):
            value = interface.get(key, "")
            if isinstance(value, str) and value and not RE_HTTPS_URL.match(value):
                errors.append(f"Invalid HTTPS URL in interface.{key}: {value}")
        default_prompt = interface.get("defaultPrompt")
        if not isinstance(default_prompt, list) or not default_prompt:
            errors.append("interface.defaultPrompt must be a non-empty list")
        else:
            for index, item in enumerate(default_prompt):
                if not isinstance(item, str) or not item.strip():
                    errors.append(f"interface.defaultPrompt[{index}] must be a non-empty string")
        capabilities = interface.get("capabilities")
        if not isinstance(capabilities, list) or not capabilities:
            errors.append("interface.capabilities must be a non-empty list")

    raw_text = PLUGIN_MANIFEST_PATH.read_text(encoding="utf-8")
    if "[TODO:" in raw_text:
        errors.append("Plugin manifest still contains placeholder TODO markers")

    if errors:
        print("Plugin manifest validation failed:\n")
        for error in errors:
            print(f"- {error}")
        return 1

    print("Plugin manifest validation passed.")
    print(f"Validated plugin manifest: {PLUGIN_MANIFEST_PATH}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
