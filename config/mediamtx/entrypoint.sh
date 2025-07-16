#!/bin/sh
envsubst < /mediamtx.template.yml > /mediamtx.yml

echo "========== GENERATED CONFIG =========="
cat /mediamtx.yml
echo "======================================"

exec /mediamtx
