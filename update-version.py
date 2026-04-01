#!/usr/bin/env python3
"""更新三个文件中的版本号

从环境变量 NEW_VERSION 或命令行参数获取新版本号，更新：
  - linglong.yaml (package.version)
  - arm64/linglong.yaml (package.version)
  - resources/usr/bin/setup-linyaps-dbus.sh (APP_VERSION)

用法:
  NEW_VERSION=2.2.1.0 ./update-version.py
  ./update-version.py 2.2.1.0
"""

import os
import sys
import re
from pathlib import Path

FILES_TO_UPDATE = [
    "linglong.yaml",
    "arm64/linglong.yaml",
    "resources/usr/bin/setup-linyaps-dbus.sh",
]


def update_version(file_path, new_version):
    with open(file_path, "r", encoding="utf-8") as f:
        content = f.read()

    # YAML: version: x.x.x.x
    content = re.sub(
        r"(  version:\s+)\d+\.\d+\.\d+\.\d+",
        rf"\g<1>{new_version}",
        content,
    )

    # Shell: APP_VERSION="x.x.x.x"
    content = re.sub(
        r'(APP_VERSION=")\d+\.\d+\.\d+\.\d+(")',
        rf"\g<1>{new_version}\g<2>",
        content,
    )

    with open(file_path, "w", encoding="utf-8") as f:
        f.write(content)

    print(f"  updated: {file_path}")


def main():
    version = os.environ.get("NEW_VERSION") or (sys.argv[1] if len(sys.argv) > 1 else "")

    if not version:
        print("错误: 请通过环境变量 NEW_VERSION 或命令行参数指定版本号", file=sys.stderr)
        sys.exit(1)

    if not re.match(r"^\d+\.\d+\.\d+\.\d+$", version):
        print(f"错误: 版本号格式不正确: {version} (需要 x.x.x.x 格式)", file=sys.stderr)
        sys.exit(1)

    root = Path(__file__).parent
    print(f"更新版本号到: {version}")

    for f in FILES_TO_UPDATE:
        update_version(root / f, version)

    print("done")


if __name__ == "__main__":
    main()
