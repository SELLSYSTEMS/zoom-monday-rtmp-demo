#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "${SCRIPT_DIR}/../.." && pwd)"

cd "${REPO_ROOT}"
. .venv/bin/activate

if [[ -f /root/.node-red/environment ]]; then
  set -a
  # shellcheck disable=SC1091
  . /root/.node-red/environment
  set +a
fi

python -m zoom_monday_rtmp_demo.cli "$@"
