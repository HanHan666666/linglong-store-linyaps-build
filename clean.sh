#!/usr/bin/env bash
set -euo pipefail

BUS_NAME="org.linglong_store.LinyapsManager"
SERV_DIR="$HOME/.config/systemd/user"
# DBUS_DIR="$HOME/.local/share/dbus-1/services"

# 停止服务（如果还在跑）
systemctl --user stop "${BUS_NAME}.service" 2>/dev/null || true

# 删除 unit 和 drop-in
rm -f "${SERV_DIR}/${BUS_NAME}.service"
rm -rf "${SERV_DIR}/${BUS_NAME}.service.d"

# 删除 dbus 激活文件
# rm -f "${DBUS_DIR}/${BUS_NAME}.service"

# 重新加载用户 systemd
systemctl --user daemon-reload

echo "已清理 ${BUS_NAME} 的用户级 systemd 和 dbus 配置"
