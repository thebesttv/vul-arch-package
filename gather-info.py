#!/bin/python

import os
import json
import csv

def get_sum(all_packages, key):
    return sum([data[key] for data in all_packages.values()])

def to_GB(bytes):
    return bytes / 1024 / 1024 / 1024

def print_stat(all_packages, msg):
    print(f'There are {len(all_packages)} {msg}')
    print(f'Receive: {to_GB(get_sum(all_packages, "receive")):.2f} GB')
    print(f'Transmit: {to_GB(get_sum(all_packages, "transmit")):.2f} GB')
    print(f'Disk: {to_GB(get_sum(all_packages, "disk")):.2f} GB')


def is_C_project(name):
    csv_file = f'arch/{name}/cloc.csv'
    if not os.path.exists(csv_file):
        return False
    with open(csv_file) as f:
        reader = csv.reader(f)
        total = 0
        c_lines = 0
        for row in reader:
            if row[1] in ('C', 'C++', 'C/C++ Header'):
                c_lines += int(row[4])
            elif row[1] == 'SUM':
                total = int(row[4])
    return total > 0 and (c_lines > 1000 or c_lines / total >= 0.4)

def get_dependencies(all_packages, top_n):
    dependencies = {}
    for name, packages in all_packages.items():
        depends = packages['depends']
        makedepends = packages['makedepends']
        for d in depends + makedepends:
            if d not in dependencies:
                dependencies[d] = 0
            dependencies[d] += 1

    dependencies = sorted(dependencies.items(), key=lambda x: x[1], reverse=True)
    return dependencies[:top_n]

if __name__ == '__main__':
    all_c_packages = {}

    # list all dirs under arch/
    for name in os.listdir('arch'):
        # list all files under arch/$name
        with open(f'arch/{name}/metrics.json') as f:
            packages = json.load(f)
            if name.startswith('lib32-'):
                continue
            if not is_C_project(name):
                continue
            all_c_packages[name] = packages

    print_stat(all_c_packages, 'C/C++ projects')

    for name in sorted(all_c_packages):
        version = all_c_packages[name]['version']
        print(name, version)

    top_n = 300
    dependencies = get_dependencies(all_c_packages, top_n)

    print(f'Top {top_n} dependencies:')

    # for name, count in dependencies:
    #     print(f'{name} {count}')
    # print()

    for name, count in dependencies:
        print(f'{name}', end=' ')
    print()

    # 磁盘占用不准确
    # print(f'Disk: {to_GB(get_sum(all_packages, "disk")):.2f} GB')
