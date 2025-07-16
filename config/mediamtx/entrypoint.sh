#!/bin/sh

# Подставим переменные окружения в шаблон
envsubst < /mediamtx.template.yml > /mediamtx.yml

# Запускаем Mediamtx с готовым файлом
exec /mediamtx
