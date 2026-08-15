#!/usr/bin/env python3
"""Validate plugin.json (and optional mcp.json) against the Agent Plugins v1.0.0 JSON Schemas.

Positive: this package's own manifests must validate.
Negative: a battery of known-bad inputs must be rejected with the expected
spec-section violation, so the schemas are proven to enforce the rules.
mcp.json is OPTIONAL per the spec (§6.2 — clients MUST NOT error on a missing
fixed component location). When present, it is validated too.

Run from the repo root:

    python3 scripts/validate-plugin.py
"""
from __future__ import annotations

import copy
import json
import sys
from pathlib import Path

from jsonschema import Draft202012Validator

ROOT = Path(__file__).resolve().parents[1]
SCHEMAS = ROOT / "scripts" / "schemas"
PLUGIN_JSON = ROOT / "plugin.json"
MCP_JSON = ROOT / "mcp.json"


def _load(name: str):
    return json.loads((SCHEMAS / name).read_text())


def _expect_rejected(label: str, schema, data) -> bool:
    errs = list(Draft202012Validator(schema).iter_errors(data))
    if not errs:
        print(f"FAIL  rejected: {label}  (schema accepted bad data)")
        return False
    print(f"PASS  rejected: {label}  ({len(errs)} error(s))")
    return True


def _expect_accepted(label: str, schema, data) -> bool:
    errs = list(Draft202012Validator(schema).iter_errors(data))
    if errs:
        print(f"FAIL  accepted: {label}  ->  {errs[0].message[:120]}")
        return False
    print(f"PASS  accepted: {label}")
    return True


def main() -> int:
    plugin_schema = _load("plugin.schema.json")
    mcp_schema = _load("mcp.schema.json")
    plugin_data = json.loads(PLUGIN_JSON.read_text())

    ok = True
    ok &= _expect_accepted("plugin.json", plugin_schema, plugin_data)

    # §5.5 name regex
    for bad_name in ("My-Plugin", "has--double", "-leading", "too.many..dots", "x" * 65):
        bad = copy.deepcopy(plugin_data)
        bad["name"] = bad_name
        ok &= _expect_rejected(f"plugin name {bad_name!r} (§5.5)", plugin_schema, bad)

    # §5.2 closed top-level
    bad = copy.deepcopy(plugin_data)
    bad["unknown"] = 1
    ok &= _expect_rejected("plugin.json unknown top-level (§5.2)", plugin_schema, bad)

    # §5.3 required fields
    for field in ("$schema", "name"):
        bad = copy.deepcopy(plugin_data)
        bad.pop(field)
        ok &= _expect_rejected(f"plugin.json missing {field} (§5.3)", plugin_schema, bad)

    # §5.4 author shape
    bad = copy.deepcopy(plugin_data)
    bad["author"] = {"name": "X", "phone": "123"}
    ok &= _expect_rejected("plugin.json author extra field (§5.4)", plugin_schema, bad)

    # mcp.json — optional. If present, validate it and the §7.2 / §9.1 negative battery.
    if MCP_JSON.exists():
        mcp_data = json.loads(MCP_JSON.read_text())
        ok &= _expect_accepted("mcp.json", mcp_schema, mcp_data)

        # §7.2.1 MCP server variants
        bad = copy.deepcopy(mcp_data)
        bad["mcpServers"]["conformance-helper"]["type"] = "websocket"
        ok &= _expect_rejected("mcp.json unknown transport (§7.2.1)", mcp_schema, bad)

        bad = copy.deepcopy(mcp_data)
        bad["mcpServers"]["conformance-helper"]["cwd"] = "/etc"
        ok &= _expect_rejected("mcp.json cwd not plugin-relative (§7.2.1)", mcp_schema, bad)

        # §9.1 reserved env keys
        for reserved in ("PLUGIN_ROOT", "PLUGIN_DATA"):
            bad = copy.deepcopy(mcp_data)
            bad["mcpServers"]["conformance-helper"]["env"][reserved] = "/oops"
            ok &= _expect_rejected(f"mcp.json env {reserved} reserved (§9.1)", mcp_schema, bad)

        bad = copy.deepcopy(mcp_data)
        bad.pop("$schema")
        ok &= _expect_rejected("mcp.json missing $schema (§7.2.1)", mcp_schema, bad)

        bad = copy.deepcopy(mcp_data)
        bad["mcpServers"]["conformance-helper"].pop("command")
        ok &= _expect_rejected("mcp.json stdio missing command (§7.2.1)", mcp_schema, bad)

        # §4.1 path containment (not in JSON Schema — checked at runtime by clients)
        plugin_root = ROOT.resolve()
        for name, srv in mcp_data["mcpServers"].items():
            if srv.get("type") != "stdio":
                continue
            cmd = srv.get("command", "")
            if not cmd.startswith("./"):
                continue
            target = (plugin_root / cmd[2:]).resolve()
            try:
                target.relative_to(plugin_root)
                print(f"PASS  containment: {name} command resolves inside plugin root")
            except ValueError:
                print(f"FAIL  containment: {name} command escapes plugin root -> {target}")
                ok = False
    else:
        print("SKIP  mcp.json not present (§6.2 — clients MUST NOT error on missing location)")

    print()
    print("ALL PASS" if ok else "FAILURES PRESENT")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
