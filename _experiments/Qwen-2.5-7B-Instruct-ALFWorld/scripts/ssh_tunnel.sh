#!/usr/bin/env bash
# Optional: run ALFWorld + this harness on your laptop, vLLM on the remote 3090.
#
#   REMOTE=user@host bash scripts/ssh_tunnel.sh
#
# Then keep api_base = http://localhost:8000/v1 in the config.
# Prefer this over exposing vLLM's port to the public internet.
set -euo pipefail

REMOTE="${REMOTE:?set REMOTE=user@host}"
LOCAL_PORT="${LOCAL_PORT:-8000}"
REMOTE_PORT="${REMOTE_PORT:-8000}"

echo "forwarding localhost:${LOCAL_PORT} -> ${REMOTE}:localhost:${REMOTE_PORT}"
exec ssh -N -L "${LOCAL_PORT}:localhost:${REMOTE_PORT}" "${REMOTE}"
