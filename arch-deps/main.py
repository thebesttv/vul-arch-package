import os
import json
import subprocess

import sys
sys.path.append('..')
from config import logging
logger = logging.getLogger('deps')

def get_all_packages(arch_txt):
    # if file not exist, return empty packages
    if not os.path.isfile(arch_txt):
        return {}
    packages = {}
    with open(arch_txt, 'r') as file:
        for line in file:
            name, version = line.strip().split()
            packages[name] = version
    return packages

def clone_package(name, version):
    cmd = f'pkgctl repo clone --switch {version} {name}'
    result = subprocess.run(cmd, shell=True)
    return result.returncode

def get_deps(name):
    cmd = f'cd {name} && env -i ../get-deps'
    result = subprocess.run(cmd, shell=True,
                            stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    if result.returncode != 0:
        return None

    return result.stdout

def handle_package(name, version):
    if clone_package(name, version) != 0:
        # failed to clone
        logger.error(f"Failed to clone {name} {version}")
        return None

    deps = get_deps(name)
    if not deps:
        return None

    deps = deps.split()
    assert len(deps) == 2
    depends, makedepends = [json.loads(s) for s in deps]

    return {
        'name': name,
        'version': version,
        'depends': depends,
        'makedepends': makedepends
    }

if __name__ == "__main__":
    all_packages = get_all_packages('../arch.txt')

    stat = []
    total = len(all_packages)
    for i, (name, version) in enumerate(all_packages.items()):
        logger.info(f'[{i}/{total}] {name} {version}')
        res = handle_package(name, version)
        if res:
            stat.append(res)

    with open('arch-deps.json', 'w') as f:
        json.dump(stat, f, indent=2)
