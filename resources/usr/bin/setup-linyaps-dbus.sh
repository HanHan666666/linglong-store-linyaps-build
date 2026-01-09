#!/usr/bin/env bash
set -euo pipefail
export DBUS_SYSTEM_BUS_ADDRESS=unix:path=/run/user/1000/bus
BUS_NAME="org.linglong_store.LinyapsManager"
BIN_DIR="$HOME/.linglong-store-v2"
BIN="$BIN_DIR/linyaps-dbus-server"
SERV_DIR="$HOME/.config/systemd/user"
VERSION_FILE="$BIN_DIR/.version"

# 改了脚本一定要改版本号
APP_VERSION="2.0.0.7"

# APP_FILE_DIR="/opt/apps/com.dongpl.linglong-store.v2/files"

mkdir -p "$BIN_DIR"

# 检查版本号是否变化
NEED_RESTART=false
if [ -f "$VERSION_FILE" ]; then
  SAVED_VERSION=$(cat "$VERSION_FILE")
  if [ "$SAVED_VERSION" != "$APP_VERSION" ]; then
    echo "检测到应用更新: $SAVED_VERSION -> $APP_VERSION"
    NEED_RESTART=true
  else
    echo "应用版本未变化: $APP_VERSION"
  fi
else
  echo "首次运行，设置版本: $APP_VERSION"
  NEED_RESTART=true
fi

if [ "$NEED_RESTART" = true ]; then
  rm -rf "$BIN_DIR/linyaps-dbus-server"
  cp /opt/apps/com.dongpl.linglong-store.v2/files/bin/linyaps-dbus-server "$BIN_DIR"
  echo "$APP_VERSION" > "$VERSION_FILE"
  echo "已更新可执行文件到版本: $APP_VERSION"
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

# 只有在需要重启时才退出并重启服务
if [ "$NEED_RESTART" = true ]; then
  echo "应用已更新，需要重启 DBus 服务..."
  # 重新加载 systemd 用户服务
  dbus-send --session \
    --dest=${BUS_NAME} \
    --type=method_call \
    /org/linglong_store/LinyapsManager \
    ${BUS_NAME}.Quit || true
  
  dbus-send --session \
    --dest=${BUS_NAME} \
    --type=method_call \
    /org/linglong_store/LinyapsManager \
    ${BUS_NAME}.Ping || true
    sleep 1
else
  echo "应用版本未变化，跳过服务重启"
fi


echo "已配置 ${BUS_NAME}"

echo "测试调用：dbus-send --session --print-reply \
  --dest=${BUS_NAME} \
  /org/linglong_store/LinyapsManager \
  ${BUS_NAME}.Ping
"

dbus-send --session \
  --dest=${BUS_NAME} \
  --type=method_call \
  /org/linglong_store/LinyapsManager \
  ${BUS_NAME}.Ping || true

sleep 0.5

export LINYAPS_CONTAINER=yes

linglong-store