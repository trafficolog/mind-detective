#!/usr/bin/env bash
# Smoke test for the Mind Detective n8n workflow.
# Usage: ./smoke-test.sh https://n8n.example.com <webhook-token> [audio-file]
set -euo pipefail
BASE="${1:?n8n base URL}"; BASE="${BASE%/}"
TOKEN="${2:?webhook token}"
AUDIO="${3:-}"

echo "md-propose:"
curl -sS -w '  [HTTP %{http_code}]\n' -X POST "$BASE/webhook/md-propose" \
  -H "Authorization: Bearer $TOKEN" -H 'Content-Type: application/json' \
  -d '{"prompt":"Верни только JSON: {\"kind\":\"question\",\"text\":\"Проверка связи\"}"}'

echo "md-propose without token (expect 403):"
curl -sS -o /dev/null -w '  [HTTP %{http_code}]\n' -X POST "$BASE/webhook/md-propose" \
  -H 'Content-Type: application/json' -d '{"prompt":"x"}'

echo "CORS preflight (expect 204 and Access-Control-Allow-Origin):"
curl -sS -i -X OPTIONS "$BASE/webhook/md-propose" -H 'Origin: http://localhost:3000' \
  -H 'Access-Control-Request-Method: POST' -H 'Access-Control-Request-Headers: authorization,content-type' \
  | grep -iE '^HTTP|access-control-allow-origin' || true

if [[ -n "$AUDIO" ]]; then
  echo "md-transcribe:"
  curl -sS -w '  [HTTP %{http_code}]\n' -X POST "$BASE/webhook/md-transcribe" \
    -H "Authorization: Bearer $TOKEN" -F "file=@$AUDIO" -F model=whisper-1 -F language=ru
fi
