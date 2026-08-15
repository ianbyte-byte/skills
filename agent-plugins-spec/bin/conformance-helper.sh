#!/usr/bin/env sh
# Sample stdio MCP server entry point for the Agent Plugins v1.0.0 conformance sample.
# Real consumers replace this with their own bundled executable.
# Per spec §7.2.1: command is a single token; args are passed separately.

set -eu

PLUGIN_ROOT_ARG=""
DATA_ARG=""

while [ "$#" -gt 0 ]; do
  case "$1" in
    --plugin-root) PLUGIN_ROOT_ARG="$2"; shift 2 ;;
    --data)        DATA_ARG="$2"; shift 2 ;;
    *)             shift ;;
  esac
done

# Client-provided env vars (spec §9.1)
echo "plugin_root=${PLUGIN_ROOT:-<unset>}"
echo "plugin_data=${PLUGIN_DATA:-<unset>}"
echo "argv_plugin_root=${PLUGIN_ROOT_ARG:-<unset>}"
echo "argv_data=${DATA_ARG:-<unset>}"
echo "log_level=${LOG_LEVEL:-info}"
