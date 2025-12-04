#!/usr/bin/env bash
set -euo pipefail
export DBUS_SYSTEM_BUS_ADDRESS=unix:path=/run/user/1000/bus
BUS_NAME="org.linglong_store.LinyapsManager"
BIN_DIR="$HOME/.linglong-store-v2"
BIN="$BIN_DIR/linyaps-dbus-server"
SERV_DIR="$HOME/.config/systemd/user"

# APP_FILE_DIR="/opt/apps/com.dongpl.linglong-store.v2/files"

mkdir -p "$BIN_DIR"
if [ ! -f "$BIN_DIR/linyaps-dbus-server" ]; then
    cp /opt/apps/com.dongpl.linglong-store.v2/files/bin/linyaps-dbus-server "$BIN_DIR"
fi

if [ ! -x "$BIN" ]; then
  echo "找不到可执行文件: $BIN"
  exit 1
fi



mkdir -p "$SERV_DIR" 

cat > "$SERV_DIR/${BUS_NAME}.service" <<EOF
[Unit]
Description=Linyaps Manager Service (User)
After=dbus.socket

[Service]
Type=dbus
BusName=${BUS_NAME}
Environment=DBUS_SESSION_BUS_ADDRESS=unix:path=%t/bus
ExecStart=${BIN}
# Restart=on-failure

[Install]
WantedBy=default.target
EOF

# cat > "$DBUS_DIR/${BUS_NAME}.service" <<EOF
# [D-BUS Service]
# Name=${BUS_NAME}
# SystemdService=${BUS_NAME}.service
# EOF



echo "已配置 ${BUS_NAME}"
echo "测试调用：dbus-send --session --print-reply --dest=${BUS_NAME} /org/linglong_store/LinyapsManager ${BUS_NAME}.Help"
dbus-send --session --print-reply --dest=${BUS_NAME} /org/linglong_store/LinyapsManager ${BUS_NAME}.Help || true

sleep 0.5
linglong-store