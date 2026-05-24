#!/usr/bin/env python3
"""自动从 GitHub Release 拉取最新版本并更新 linglong.yaml

当前会为 linglong-store 选择上游 Release 中的 .deb 产物，
而不是 AppImage。

用法:
  ./update-from-github-release.py           # 更新所有架构
  ./update-from-github-release.py x86_64    # 只更新 x86_64
  ./update-from-github-release.py aarch64   # 只更新 aarch64 (arm64)
"""

import sys
from pathlib import Path
from urllib.request import urlopen, Request
from urllib.error import URLError
import json

# 颜色输出
class Colors:
    GREEN = '\033[0;32m'
    YELLOW = '\033[1;33m'
    RED = '\033[0;31m'
    BLUE = '\033[0;34m'
    NC = '\033[0m'

def print_green(msg):
    print(f"{Colors.GREEN}{msg}{Colors.NC}")

def print_yellow(msg):
    print(f"{Colors.YELLOW}{msg}{Colors.NC}")

def print_red(msg):
    print(f"{Colors.RED}{msg}{Colors.NC}")

def print_blue(msg):
    print(f"{Colors.BLUE}{msg}{Colors.NC}")

def normalize_digest(digest):
    """规范化 GitHub API 返回的 digest 字段"""
    if digest.startswith('sha256:'):
        return digest[7:]
    return digest

def asset_name_matches(asset_name, file_pattern):
    """检查资源名称是否匹配指定模式

    file_pattern 支持以下两种形式：
    - 字符串：只要资产名包含该子串即可
    - 字典：支持 contains / suffix 组合匹配
    """
    if isinstance(file_pattern, str):
        return file_pattern in asset_name

    contains = file_pattern.get('contains', [])
    suffix = file_pattern.get('suffix')

    if suffix and not asset_name.endswith(suffix):
        return False

    return all(pattern in asset_name for pattern in contains)

def format_file_pattern(file_pattern):
    """将文件匹配模式格式化为可读字符串"""
    if isinstance(file_pattern, str):
        return file_pattern

    contains = ' + '.join(file_pattern.get('contains', []))
    suffix = file_pattern.get('suffix', '')

    if contains and suffix:
        return f"{contains} + endswith({suffix})"
    if suffix:
        return f"endswith({suffix})"
    return contains

def fetch_github_release(repo):
    """获取 GitHub 仓库的最新 Release 信息"""
    url = f"https://api.github.com/repos/{repo}/releases/latest"
    req = Request(url)
    req.add_header('User-Agent', 'Mozilla/5.0')

    try:
        with urlopen(req, timeout=30) as response:
            data = json.loads(response.read().decode())
            return data
    except URLError as e:
        print_red(f"获取 {repo} Release 信息失败: {e}")
        sys.exit(1)
    except json.JSONDecodeError as e:
        print_red(f"解析 JSON 失败: {e}")
        sys.exit(1)

def get_asset_info(release_data, file_pattern):
    """从 Release 数据中获取匹配的资源信息"""
    for asset in release_data.get('assets', []):
        if asset_name_matches(asset['name'], file_pattern):
            return {
                'url': asset['browser_download_url'],
                'digest': normalize_digest(asset.get('digest', ''))
            }
    return None

def update_yaml_file(yaml_path, sources_config):
    """更新 linglong.yaml 文件中的 sources 部分，只更新指定的 name 条目"""

    with open(yaml_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # 将更新配置转换为字典，方便查找
    update_dict = {item['name']: item for item in sources_config}

    # 按行分割内容
    lines = content.split('\n')

    # 遍历每一行，找到需要更新的条目
    i = 0
    while i < len(lines):
        line = lines[i]

        # 检查是否是 name 行
        if line.strip().startswith('name:'):
            name_value = line.split(':', 1)[1].strip()

            # 如果这个 name 需要更新
            if name_value in update_dict:
                update_item = update_dict[name_value]

                # 找到这个 source 块的开始（往回找最近的 '- kind:'）
                j = i
                while j >= 0 and not lines[j].strip().startswith('- kind:'):
                    j -= 1

                if j >= 0:
                    # 更新这个 source 块的 url 和 digest
                    k = j + 1
                    while k < len(lines) and not lines[k].strip().startswith('- kind:'):
                        if lines[k].strip().startswith('url:'):
                            lines[k] = f'    url: {update_item["url"]}'
                        elif lines[k].strip().startswith('digest:'):
                            lines[k] = f'    digest: {update_item["digest"]}'

                        k += 1

        i += 1

    # 重新组合内容
    new_content = '\n'.join(lines)

    # 写入新内容
    with open(yaml_path, 'w', encoding='utf-8') as f:
        f.write(new_content)

def update_architecture(arch, arch_config, releases):
    """更新指定架构的配置文件"""
    repo_root = Path(__file__).resolve().parent
    yaml_path = repo_root / arch_config['dir'] / "linglong.yaml"

    if not yaml_path.exists():
        print_red(f"  未找到配置文件: {yaml_path}")
        return False

    print_yellow(f"\n处理架构 {arch}:")

    sources_config = []

    for file_info in arch_config['files']:
        name = file_info['name']
        repo_key = file_info['repo']
        pattern = file_info['pattern']

        release_data = releases[repo_key]
        asset_info = get_asset_info(release_data, pattern)

        if not asset_info:
            print_red(f"  未找到文件: {format_file_pattern(pattern)}")
            return False

        print(f"  {name}:")
        print(f"    url: {asset_info['url']}")
        print(f"    digest: {asset_info['digest']}")

        sources_config.append({
            'name': name,
            'url': asset_info['url'],
            'digest': asset_info['digest']
        })

    # 更新 YAML 文件
    update_yaml_file(yaml_path, sources_config)
    print_green(f"  ✓ 已更新: {yaml_path}")

    return True

def main():
    print_green("=== GitHub Release 多架构自动更新脚本 ===\n")

    # 解析命令行参数
    arch_args = sys.argv[1:] if len(sys.argv) > 1 else []

    # 仓库配置
    repos = {
        'store': 'HanHan666666/flutter-linglong-store',
        'manager': 'guanzi008/org.linglong-store.LinyapsManager'
    }

    # 架构配置
    architectures = {
        'x86_64': {
            'dir': '.',  # 根目录
            'files': [
                {
                    'name': 'linglong-store',
                    'repo': 'store',
                    'pattern': {
                        'contains': ['linglong-store_'],
                        'suffix': '_amd64.deb'
                    }
                },
                {
                    'name': 'linyaps-dbus-server',
                    'repo': 'manager',
                    'pattern': 'linyaps-dbus-server-linux-amd64'
                },
                {
                    'name': 'linyapsctl',
                    'repo': 'manager',
                    'pattern': 'linyapsctl-linux-amd64'
                }
            ]
        },
        'aarch64': {
            'dir': 'arm64',
            'files': [
                {
                    'name': 'linglong-store',
                    'repo': 'store',
                    'pattern': {
                        'contains': ['linglong-store_'],
                        'suffix': '_arm64.deb'
                    }
                },
                {
                    'name': 'linyaps-dbus-server',
                    'repo': 'manager',
                    'pattern': 'linyaps-dbus-server-linux-arm64'
                },
                {
                    'name': 'linyapsctl',
                    'repo': 'manager',
                    'pattern': 'linyapsctl-linux-arm64'
                }
            ]
        }
    }

    # 确定要更新的架构
    if arch_args:
        # 验证指定的架构
        valid_archs = tuple(architectures.keys())
        normalized_archs = []

        for arch in arch_args:
            normalized_archs.append('aarch64' if arch == 'arm64' else arch)

        invalid = sorted({arch for arch in normalized_archs if arch not in architectures})
        if invalid:
            print_red(f"错误: 不支持的架构: {', '.join(invalid)}")
            print_yellow(f"支持的架构: {', '.join(valid_archs)}")
            sys.exit(1)

        requested_archs = set(normalized_archs)
        archs_to_update = [arch for arch in architectures.keys() if arch in requested_archs]
    else:
        # 更新所有架构
        archs_to_update = list(architectures.keys())

    print_blue(f"将更新架构: {', '.join(archs_to_update)}\n")

    # 获取 Release 信息
    print_yellow("1. 获取 GitHub Release 最新版本...")
    releases = {}

    for key, repo in repos.items():
        releases[key] = fetch_github_release(repo)
        version = releases[key]['tag_name']
        print_green(f"  {repo}: {version}")

    # 更新每个架构
    print_yellow("\n2. 更新各架构配置文件...")

    success_count = 0
    for arch in archs_to_update:
        if update_architecture(arch, architectures[arch], releases):
            success_count += 1

    # 总结
    print_green(f"\n✓ 更新完成! 成功: {success_count}/{len(archs_to_update)}")

if __name__ == '__main__':
    main()
