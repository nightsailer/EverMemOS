#!/usr/bin/env python3
"""分析 src 目录下的所有包和模块结构"""
import os
from pathlib import Path
from collections import defaultdict

def analyze_src_structure(src_path):
    """分析源码目录结构"""
    src_root = Path(src_path)

    # 存储包和单文件模块
    packages = []  # 包含 __init__.py 的目录
    single_modules = []  # 独立的 .py 文件

    # 遍历所有目录
    for root, dirs, files in os.walk(src_root):
        root_path = Path(root)
        rel_path = root_path.relative_to(src_root)

        # 检查是否是包（包含 __init__.py）
        if '__init__.py' in files:
            # 计算深度
            depth = len(rel_path.parts) if str(rel_path) != '.' else 0

            # 获取包中的 .py 文件（排除 __init__.py 和测试文件）
            py_files = [f for f in files
                       if f.endswith('.py')
                       and f != '__init__.py'
                       and not f.startswith('test_')]

            packages.append({
                'path': str(rel_path) if str(rel_path) != '.' else 'src',
                'full_path': str(root_path),
                'depth': depth,
                'modules': py_files,
                'subdirs': [d for d in dirs if not d.startswith('__')]
            })

    return sorted(packages, key=lambda x: (x['depth'], x['path']))

def print_structure(packages):
    """打印目录结构"""
    print("=" * 80)
    print("EverMemOS 源码模块结构分析")
    print("=" * 80)
    print(f"\n总计: {len(packages)} 个包\n")

    # 按深度分组
    by_depth = defaultdict(list)
    for pkg in packages:
        by_depth[pkg['depth']].append(pkg)

    for depth in sorted(by_depth.keys()):
        print(f"\n{'='*80}")
        print(f"层级 {depth} - {len(by_depth[depth])} 个包")
        print(f"{'='*80}")

        for pkg in by_depth[depth]:
            indent = "  " * depth
            path = pkg['path']
            modules_count = len(pkg['modules'])
            subdirs_count = len(pkg['subdirs'])

            print(f"{indent}📦 {path}/")
            if modules_count > 0:
                print(f"{indent}   ├─ {modules_count} 个模块文件")
                for mod in pkg['modules'][:3]:  # 只显示前3个
                    print(f"{indent}   │  • {mod}")
                if modules_count > 3:
                    print(f"{indent}   │  ... 还有 {modules_count - 3} 个")
            if subdirs_count > 0:
                print(f"{indent}   └─ {subdirs_count} 个子包")

def generate_doc_plan(packages):
    """生成文档编写计划"""
    print("\n" + "=" * 80)
    print("文档编写计划")
    print("=" * 80)
    print("\n每个包需要创建: specs/ac_mod/{包路径}.ac.mod.md\n")

    # 按主要模块分组
    top_level = defaultdict(list)
    for pkg in packages:
        parts = pkg['path'].split('/')
        if len(parts) > 0 and parts[0] != 'src':
            top_level[parts[0]].append(pkg)
        else:
            top_level['根目录'].append(pkg)

    doc_count = 0
    for module_name in sorted(top_level.keys()):
        pkgs = top_level[module_name]
        print(f"\n## {module_name} ({len(pkgs)} 个包)")
        print("-" * 80)
        for pkg in pkgs:
            doc_path = f"specs/ac_mod/{pkg['path'].replace('/', '.')}.ac.mod.md"
            print(f"  • {pkg['path']:60s} → {doc_path}")
            doc_count += 1

    print(f"\n{'='*80}")
    print(f"总计需要编写: {doc_count} 个 .ac.mod.md 文档")
    print(f"{'='*80}")

if __name__ == '__main__':
    src_path = '/home/user/EverMemOS/src'
    packages = analyze_src_structure(src_path)
    print_structure(packages)
    generate_doc_plan(packages)
