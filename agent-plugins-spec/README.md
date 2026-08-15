# Agent Plugins Spec Support

WIP branch: `feat/agent-plugins-spec`

Target: conform this repo to the [Agent Plugins v1.0.0](https://agent-plugins.org/specification) package format.

## Why a subdirectory

Isolates the spec-compliance work from the rest of the fork so pulling upstream
into `main` stays clean. Once the changes here are reviewed and approved they
can be promoted to repo root in a follow-up PR.

## Layout

```
agent-plugins-spec/
├── README.md                                # this file
├── NOTES.md                                 # decisions + open questions
├── plugin.json                              # Agent Plugins v1.0.0 manifest
├── mcp.json                                 # stdio + streamable-http servers
├── .schemas/                                # cached official JSON Schemas
│   ├── plugin.schema.json
│   └── mcp.schema.json
├── skills/
│   └── agent-plugins-audit/
│       └── SKILL.md                         # one skill (§7.1)
└── bin/
    └── conformance-helper.sh                # stdio MCP server stub (§7.2.1)
```

## Conformance status

Validated against the official JSON Schemas (`https://agent-plugins.org/schemas/1.0.0/`).
**18/18** positive + negative tests pass — see `NOTES.md` for the list and what
the schemas do *not* cover (runtime containment, placeholder expansion
behavior, etc.).

### §5 Manifest

- [x] `plugin.json` at plugin root, valid JSON, object type
- [x] Required `$schema` and `name` present
- [x] `name` matches §5.5 regex (lowercase, alphanumeric+`-`/`.`, no `--`/`..`, alphanumeric start/end, ≤ 64 chars)
- [x] No unknown top-level fields (`additionalProperties: false`)
- [x] Author has only `name` / `email` / `url`
- [ ] `extensions` — intentionally omitted until authoritative client namespace is known (see `NOTES.md`)

### §6 / §7 Component discovery

- [x] Skills discovered from fixed `skills/` location
- [x] MCP servers loaded only from `mcp.json`
- [x] `mcpServers` is an object, each entry is one of stdio / streamable-http / sse
- [x] stdio `command` is plugin-relative (`./bin/conformance-helper.sh`)
- [x] stdio `cwd` matches `^(?:\./|\$\{PLUGIN_ROOT\}(?:/|$)|\$\{PLUGIN_DATA\}(?:/|$))`
- [x] stdio `env` has no reserved `PLUGIN_ROOT` / `PLUGIN_DATA` keys
- [x] streamable-http `url` is absolute, no user info, no fragment (example.com placeholder)

### §9 Environment & expansion

- [x] `${PLUGIN_ROOT}` and `${PLUGIN_DATA}` only used in `args` / `env` / `cwd` (never in `command`, `url`, header names/values)
- [x] No nested or recursive placeholder forms
- [x] No secrets in `env` or `headers`

### §11 Client conformance (this package's obligations, not the client's)

- [x] At least one component type supported (skills + MCP)
- [x] Plugin-relative paths begin with `./` and resolve inside the plugin root
- [x] No symlinks in the package
- [x] `$schema` value uses the canonical 1.0.0 identifier

## How to validate locally

```sh
python3 /tmp/validate_plugin_negatives.py
```

Re-runs the schema validation suite (positive + negative) and prints one line per check.

## Status

Sample package layout is in place and validates. Open questions are in `NOTES.md`.
