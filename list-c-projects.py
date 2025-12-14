#!/usr/bin/env python3
"""
遍历arch下的项目的cloc.csv，列出所有C语言项目。
标准：项目中C的占比至少50%
"""

import os
import csv
import sys

def parse_cloc_csv(csv_file):
    """
    解析cloc.csv文件，返回各语言的代码行数
    
    Returns:
        dict: 语言名称到代码行数的映射
        int: 总代码行数
    """
    if not os.path.exists(csv_file):
        return None, 0
    
    language_stats = {}
    total_lines = 0
    
    try:
        with open(csv_file, 'r', encoding='utf-8') as f:
            reader = csv.reader(f)
            for row in reader:
                # 跳过表头和空行
                if len(row) < 5 or row[1] == 'language':
                    continue
                
                language = row[1]
                
                # 提取代码行数（第5列，索引4）
                try:
                    code_lines = int(row[4])
                except (ValueError, IndexError):
                    continue
                
                if language == 'SUM':
                    total_lines = code_lines
                else:
                    language_stats[language] = code_lines
    except Exception as e:
        print(f"Error parsing {csv_file}: {e}", file=sys.stderr)
        return None, 0
    
    return language_stats, total_lines

def is_c_project(project_name, arch_dir='arch'):
    """
    判断项目是否是C语言项目（C语言代码占比至少50%）
    
    Args:
        project_name: 项目名称
        arch_dir: arch目录路径
    
    Returns:
        tuple: (是否是C项目, C代码行数, 总代码行数, C语言占比)
    """
    csv_file = os.path.join(arch_dir, project_name, 'cloc.csv')
    
    language_stats, total_lines = parse_cloc_csv(csv_file)
    
    if language_stats is None or total_lines == 0:
        return False, 0, 0, 0.0
    
    # 获取C语言的代码行数
    c_lines = language_stats.get('C', 0)
    
    # 计算C语言占比
    c_percentage = (c_lines / total_lines * 100) if total_lines > 0 else 0
    
    # 判断是否满足条件：C语言占比至少50%
    is_c = c_percentage >= 50.0
    
    return is_c, c_lines, total_lines, c_percentage

def main():
    """主函数：遍历所有项目，找出C语言项目"""
    arch_dir = 'arch'
    
    if not os.path.isdir(arch_dir):
        print(f"错误：找不到目录 {arch_dir}", file=sys.stderr)
        sys.exit(1)
    
    # 存储所有C语言项目
    c_projects = []
    
    # 遍历arch目录下的所有项目
    for project_name in sorted(os.listdir(arch_dir)):
        project_path = os.path.join(arch_dir, project_name)
        
        # 跳过非目录
        if not os.path.isdir(project_path):
            continue
        
        # 判断是否是C语言项目
        is_c, c_lines, total_lines, c_percentage = is_c_project(project_name, arch_dir)
        
        if is_c:
            c_projects.append({
                'name': project_name,
                'c_lines': c_lines,
                'total_lines': total_lines,
                'percentage': c_percentage
            })
    
    # 输出结果
    print(f"# C语言项目列表（C语言占比 ≥ 50%）")
    print(f"# 共找到 {len(c_projects)} 个C语言项目")
    print()
    
    for project in c_projects:
        # 读取版本信息
        version_file = os.path.join(arch_dir, project['name'], 'version')
        version = ''
        if os.path.exists(version_file):
            try:
                with open(version_file, 'r') as f:
                    version = f.read().strip()
            except:
                pass
        
        # 输出项目名称和版本
        if version:
            print(f"{project['name']} {version}")
        else:
            print(f"{project['name']}")

if __name__ == '__main__':
    main()
