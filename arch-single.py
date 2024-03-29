#!/bin/python

import os
import random
import subprocess
import shutil

import config

from config import logging
logger = logging.getLogger('arch-single')

def is_github_actions():
    github_actions = os.environ.get('GITHUB_ACTIONS')
    return github_actions is not None and github_actions == 'true'

def get_tag_of_repo(repo_path):
    try:
        # 执行 git describe 命令，获取标签信息
        result = subprocess.check_output(
            ['git', 'describe', '--tags', '--exact-match'],
            cwd=repo_path, stderr=subprocess.STDOUT, text=True
        )
        return result.strip()
    except subprocess.CalledProcessError:
        return ''

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

def get_existing_packages(all_packages, pkg_root_dir):
    packages = set()
    for name in os.listdir(pkg_root_dir):
        packages.add(name)
    return packages

def move_packages_up_front(packages, keywords):
    """Move elements containing one of keywords to the front of the list"""
    def custom_sort(element):
        # 自定义排序函数，包含 keywords 的元素排在前面
        for kw in keywords:
            if kw in element:
                return 0
        return 1
    packages.sort(key=custom_sort)

def write_env_var(name, value):
    logger.info(f'  {name}={value}')
    subprocess.run(f'echo "{name}={value}" >> "$GITHUB_ENV"', shell=True, check=True)

if __name__ == "__main__":
    if is_github_actions():
        # logger.info('Running in GitHub Actions with Arch Linux Docker')
        # root = '/github/workspace'
        logger.info('Running in GitHub Actions (not with Arch Linux Docker)')
        root = config.CURRENT_DIR
    else:
        logger.info('Running on local machine')
        root = config.CURRENT_DIR
    logger.info(f'Root: {root}')

    arch_txt = os.path.join(root, 'arch.txt')
    arch_ignore = os.path.join(root, 'arch.ignore')
    pkg_dir = os.path.join(root, 'arch')
    os.makedirs(pkg_dir, exist_ok=True)

    all_packages = get_all_packages(arch_txt)
    ignored_packages = get_all_packages(arch_ignore)
    existing_packages = get_existing_packages(all_packages, pkg_dir)

    # remove ignored packages
    for name, version in ignored_packages.items():
        if name in all_packages and version == all_packages[name]:
            logger.debug(f'Ignoring: {name} {version}')
            del all_packages[name]

    missing_packages = [pkg for pkg in all_packages if pkg not in existing_packages]

    logger.info(f'All packages: {len(all_packages)}')
    logger.info(f'Existing packages: {len(existing_packages)}')
    logger.info(f'Missing: {len(missing_packages)}')

    seed = int(os.environ.get('RANDOM_SEED') or "20240202")
    logger.info(f"Random seed: {seed}")
    random.seed(seed)
    random.shuffle(missing_packages)

    # do large packages first
    move_packages_up_front(missing_packages, ['electron', 'chromium'])

    job_id = os.environ.get('JOB_ID') or "0"
    index = int(job_id)
    if index >= len(missing_packages):
        logger.info(f'Job ID {index} exceeds length of missing packages, exiting ...')
        exit(0)
    logger.info(f'Selecting {index}-th package')
    chosen_package = missing_packages[index]
    chosen_version = all_packages[chosen_package]

    logger.info(f'Randomly select a package: {chosen_package} {chosen_version}')

    if is_github_actions():
        logger.info(f'Setting environment variables for GitHub Actions:')
        write_env_var('TBT_UPDATE_PACKAGE', 'true')
        write_env_var('TBT_PACKAGE_NAME', chosen_package)
        write_env_var('TBT_PACKAGE_VERSION', chosen_version)
