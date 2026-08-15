---
name: agent-plugins-audit
description: Audit a directory against the Agent Plugins v1.0.0 specification — validate plugin.json and mcp.json against the published JSON schemas, check §4.1 path containment, verify §5.5 name constraints, and report §11 client conformance gaps. Use when a user asks whether a folder is a valid Agent Plugin package, or wants to debug a rejection from a conformant client.
---

# Agent Plugins Audit

Verify that a directory conforms to the [Agent Plugins v1.0.0](https://agent-plugins.org/specification) package format.

## Inputs

- **Plugin path** — directory to audit (defaults to the current working directory)
- **Schema cache** — local copies of `plugin.schema.json` and `mcp.schema.json` (see `../.schemas/`)

## Procedure

1. Confirm `plugin.json` exists at the plugin root (§5.1). If missing, report and stop — there is no plugin.
2. Validate `plugin.json` against `https://agent-plugins.org/schemas/1.0.0/plugin.schema.json`:
   - Required: `$schema`, `name` (§5.3)
   - `name` matches the §5.5 regex: 1–64 chars, `[a-z0-9.-]`, no `--` or `..`, alphanumeric start/end
   - No unknown top-level fields (schema has `additionalProperties: false`)
   - `extensions`, if present, is an object (§8.1) — do not validate namespace values
3. If `mcp.json` exists, validate against `https://agent-plugins.org/schemas/1.0.0/mcp.schema.json`:
   - Required: `$schema`, `mcpServers` (§7.2.1)
   - Each server matches exactly one `oneOf` variant (stdio / streamable-http / sse)
   - For stdio, `cwd` matches `^(?:\./|\$\{PLUGIN_ROOT\}(?:/|$)|\$\{PLUGIN_DATA\}(?:/|$))`
   - For stdio, `env` MUST NOT contain keys `PLUGIN_ROOT` or `PLUGIN_DATA` (§9.1)
4. Check §4.1 path containment:
   - Every `command` is either a bare token or starts with `./`
   - No relative path uses `..` to escape the plugin root
5. Skills discovery (§7.1):
   - If `skills/` exists, scan immediate children for `SKILL.md` (regular file)
   - Do not recurse deeper than one level
6. Report each check as PASS / FAIL / SKIP with the spec section cited for any FAIL.

## Output

A checklist of pass/fail lines. Failures cite the exact section (e.g. "FAIL plugin.json: name 'My-Plugin' violates §5.5 — uppercase not allowed").

## What it does not do

- Does not load the plugin in a runtime client
- Does not validate the contents of `extensions` namespace values (§8.1: client-owned)
- Does not recursively search `skills/` for nested skills (§7.1: one level only)
- Does not perform placeholder expansion (§9.2 is client behaviour)
