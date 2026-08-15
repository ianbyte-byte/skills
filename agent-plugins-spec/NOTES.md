# Conformance notes

Decisions and open questions for the `mavis-conformance-sample` package.

## Decisions

### Name: `mavis-conformance-sample`

- Matches the §5.5 regex (lowercase alphanumeric + `-`/`.`, alphanumeric start/end, no `--`/`..`).
- Signals "this folder is a *sample* of the conformant layout", not the whole repo.
- Distinct from the existing Claude Code plugin name `mattpocock-skills` in `.claude-plugin/marketplace.json`. Those two ecosystems are not required to share names; the spec only constrains the Agent Plugins `name` field.

### `extensions` left out

The spec marks `extensions` optional and the schema has no `required` entry for it. Two reasons to omit for now:

1. We do not have authoritative namespace identifiers for either Claude Code or the oh-my-claudecode tooling from a primary source. The spec says clients SHOULD base the namespace on a domain they control, but it does not publish a registry, and inventing namespaces would be wrong.
2. The spec §8.1 explicitly tells clients to ignore unimplemented namespaces, so leaving the field absent is safer than guessing.

When a real client namespace is known, add it under `extensions.<namespace>` as a JSON object.

### MCP server set: 1 stdio + 1 streamable-http

Covers both transports the spec marks as required-or-strongly-recommended (§7.2.1 transport support). `sse` is OPTIONAL and deprecated; skipped.

- `conformance-helper` (stdio): exercises `${PLUGIN_ROOT}` and `${PLUGIN_DATA}` placeholder expansion in `args` and `cwd`, and shows a plugin-relative `./bin/...` command. The script `bin/conformance-helper.sh` exists in the package and runs.
- `registry-example` (streamable-http): uses an `example.com` URL, `Accept` header, no secrets. The example domain makes the placeholder nature obvious.

### Why a subdirectory, not repo root

The user's fork must keep pulling upstream `mattpocock/skills` cleanly. The Agent Plugins v1.0.0 spec wants `plugin.json` at the **plugin root** — meaning whatever directory a conformant client loads. Putting the manifest under `agent-plugins-spec/` lets:

- Upstream syncs continue unaffected (no `plugin.json` at repo root to conflict with anything)
- The directory itself be a valid Agent Plugins package for a client that loads `agent-plugins-spec/`
- Future promotion to repo root happen in a separate, reviewable change

If/when the package is promoted to repo root, this folder can be deleted or kept as a self-contained test fixture.

## What the schema does not cover

The JSON schemas validate structure and a subset of the spec's normative rules. The runtime rules below are not in the schema; this sample does them by construction:

| Spec rule | How this sample satisfies it |
| --- | --- |
| §4.1(3) symlink/junction containment | Not exercised — package is symlink-free. |
| §4.1(4) plugin-relative paths begin with `./` | `command: "./bin/conformance-helper.sh"` does; `cwd` is `${PLUGIN_ROOT}` (also a permitted form per §7.2.1). |
| §4.1(5) opaque values are not path-checked | `args`, `env` values are not path-validated by the client. |
| §7.1 skills are immediate children of `skills/` containing `SKILL.md` | `skills/agent-plugins-audit/SKILL.md` — one level only. |
| §7.2.1(2) bare command resolved by platform | No bare commands used; all are plugin-relative. |
| §9.1 `PLUGIN_ROOT` and `PLUGIN_DATA` are client-provided | `env` for the stdio server does NOT contain these keys (schema-enforced); clients must set them. |
| §9.2 single-pass, non-recursive placeholder expansion | Strings use exactly `${PLUGIN_ROOT}` and `${PLUGIN_DATA}/conformance` — no nested forms. |
| §9.2 no expansion in `command`, `url`, header names/values | `command` is literal `./bin/conformance-helper.sh`; `url` and headers contain no placeholders. |
| §11.3 component failures non-fatal | A `bin/conformance-helper` that fails to start would not stop the skill from loading. |

## Validation evidence

Positive + negative validation against the official JSON Schemas: **18/18 tests pass** (2 accept good data, 16 reject bad data covering §5.2 unknown fields, §5.3 missing required, §5.4 author shape, §5.5 name regex (5 cases), §7.2.1 unknown transport, missing `command`/`url`, §7.2.1 cwd pattern, §9.1 reserved env keys).

Local script smoke test: `bin/conformance-helper.sh` runs and prints the expected `PLUGIN_ROOT` / `PLUGIN_DATA` values when invoked with the documented args.

## Open questions for the user

1. Should `extensions` include a `com.anthropic.claude-code` (or similar) namespace? We need a primary source for the actual namespace identifier.
2. Is the goal to (a) keep this as a *sample* subdirectory forever, or (b) eventually promote `plugin.json` and `mcp.json` to repo root and turn the whole fork into a conformant plugin?
3. The fork is currently published as a Claude Code plugin via `.claude-plugin/marketplace.json`. If we promote to root, will that marketplace config still be needed, or does Agent Plugins v1 supersede it?
