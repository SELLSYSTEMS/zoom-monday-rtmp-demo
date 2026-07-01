#!/usr/bin/env bash
set -euo pipefail

DOMAIN="mondayzoom.sellsystems.agency"
REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")"/../.. && pwd)"
RTMP_CONF_TARGET="/etc/nginx/rtmp.conf"
SITE_TARGET="/etc/nginx/sites-available/mondayzoom-hls.conf"
SITE_LINK="/etc/nginx/sites-enabled/mondayzoom-hls.conf"
NGINX_CONF="/etc/nginx/nginx.conf"
RUNTIME_DIR="/var/lib/zoom-monday-rtmp-demo"
RTMP_LISTEN_PORT="1935"

while [[ $# -gt 0 ]]; do
  case "$1" in
    --domain)
      DOMAIN="${2:?missing value for --domain}"
      shift 2
      ;;
    --rtmp-listen-port)
      RTMP_LISTEN_PORT="${2:?missing value for --rtmp-listen-port}"
      shift 2
      ;;
    *)
      echo "Unknown argument: $1" >&2
      exit 2
      ;;
  esac
done

if [[ "$(id -u)" -ne 0 ]]; then
  echo "Run as root" >&2
  exit 1
fi

export DEBIAN_FRONTEND=noninteractive

apt-get update
apt-get install -y --no-install-recommends ffmpeg libnginx-mod-rtmp

install -d -m 0755 "${RUNTIME_DIR}" "${RUNTIME_DIR}/recordings" "${RUNTIME_DIR}/hls"
chown -R www-data:www-data "${RUNTIME_DIR}"

python3 - <<PY
from pathlib import Path
source = Path("${REPO_ROOT}/deploy/nginx/rtmp.conf.example")
target = Path("${RTMP_CONF_TARGET}")
text = source.read_text()
text = text.replace("__RTMP_LISTEN_PORT__", "${RTMP_LISTEN_PORT}")
target.write_text(text)
PY
python3 - <<PY
from pathlib import Path
source = Path("${REPO_ROOT}/deploy/nginx/mondayzoom-hls-site.conf.example")
target = Path("${SITE_TARGET}")
text = source.read_text()
text = text.replace("mondayzoom.sellsystems.agency", "${DOMAIN}")
target.write_text(text)
PY

if ! grep -Fq 'include /etc/nginx/rtmp.conf;' "${NGINX_CONF}"; then
  python3 - <<'PY'
from pathlib import Path
path = Path("/etc/nginx/nginx.conf")
text = path.read_text()
needle = "\nhttp {\n"
replacement = "\ninclude /etc/nginx/rtmp.conf;\n\nhttp {\n"
if "include /etc/nginx/rtmp.conf;" not in text:
    if needle not in text:
        raise SystemExit("Could not find http block in nginx.conf")
    text = text.replace(needle, replacement, 1)
    path.write_text(text)
PY
fi

ln -sfn "${SITE_TARGET}" "${SITE_LINK}"
rm -f /etc/nginx/sites-enabled/default

nginx -t
systemctl reload nginx

echo "Bootstrap complete"
echo "Domain: ${DOMAIN}"
echo "Local RTMP listen port: ${RTMP_LISTEN_PORT}"
echo "Public RTMP ingest URL must be supplied separately from your platform's published port mapping"
echo "HLS path: http://${DOMAIN}/hls/<stream_key>.m3u8"
