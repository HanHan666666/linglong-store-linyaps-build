# linglong-store-build

玲珑应用商店社区版的玲珑包构建配置仓库。用于将上游预编译二进制文件打包为玲珑（Linglong）应用格式。

## 项目概述

本仓库**不包含应用源代码**，而是维护玲珑包的构建定义文件（`linglong.yaml`），从以下上游项目拉取预编译二进制并打包：

| 组件 | 上游仓库 | 说明 |
|------|---------|------|
| linglong-store | [SXFreell/linglong-store](https://github.com/SXFreell/linglong-store) | 玲珑商店前端（GTK4/WebKit） |
| linyaps-dbus-server | [guanzi008/org.linglong-store.LinyapsManager](https://github.com/guanzi008/org.linglong-store.LinyapsManager) | DBus 服务端，提供应用管理接口 |
| linyapsctl | 同上 | 玲珑包管理 CLI 工具，安装为 `ll-cli` |

## 支持架构

- **x86_64** — 主配置（根目录 `linglong.yaml`）
- **aarch64** — ARM64 配置（`arm64/linglong.yaml`）

## 目录结构

```
.
├── linglong.yaml              # x86_64 构建配置
├── linglong-no-gtk4.yaml      # 不依赖 GTK4 runtime 的旧版配置
├── arm64/
│   └── linglong.yaml          # aarch64 构建配置
├── resources/
│   └── usr/
│       ├── bin/setup-linyaps-dbus.sh   # DBus 服务部署与应用启动脚本
│       └── share/
│           ├── applications/linglong-store.desktop  # 桌面入口
│           ├── dbus-1/services/         # DBus 服务配置
│           └── icons/                   # 应用图标
├── rebuild.sh                 # 一键构建脚本
├── clean.sh                   # 清理构建产物与已安装服务
└── update-from-github-release.py  # 自动从 GitHub Release 更新源文件配置
```

## 构建依赖

- [ll-builder](https://github.com/nicesteven/nicesteven.github.io)（玲珑构建工具）
- deepin 25 系统环境

## 使用方法

### 构建并导出

```bash
./rebuild.sh
```

该脚本会依次执行：
1. 清理旧产物（`clean.sh`）
2. 构建 x86_64 和 aarch64 两个架构的玲珑包
3. 导出 `.uab` 和 `.layer` 文件

### 清理

```bash
./clean.sh
```

停止 DBus 服务、卸载已安装的包、删除构建产物。

### 更新上游版本

```bash
# 更新所有架构
./update-from-github-release.py

# 只更新指定架构
./update-from-github-release.py x86_64
./update-from-github-release.py aarch64
```

脚本会自动查询 GitHub Release API，获取最新版本的下载地址和摘要，更新对应的 `linglong.yaml`。

## 运行时架构

应用启动流程：

1. 系统通过 `.desktop` 文件启动 `setup-linyaps-dbus.sh`
2. 脚本将 `linyaps-dbus-server` 部署到用户目录，注册为 systemd 用户服务
3. 通过 DBus 启动管理服务
4. 在容器环境中启动 `linglong-store` 前端

## 版本

当前版本：**2.2.0.1**

基础环境：
- Base: `org.deepin.base/25.2.2`
- Runtime: `org.deepin.runtime.gtk4/25.2.2`
