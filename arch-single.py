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
    packages = {}
    with open(arch_txt, 'r') as file:
        for line in file:
            name, version = line.strip().split()
            packages[name] = version
    return packages

def get_existing_packages(all_packages, pkg_root_dir):
    packages = {}
    for name in os.listdir(pkg_root_dir):
        pkg_dir = os.path.join(pkg_root_dir, name)
        version_file = os.path.join(pkg_dir, 'version')

        # non-existent package
        if name not in all_packages:
            logger.warning(f'Package {name} is not in all packages! removed')
            shutil.rmtree(pkg_dir)
            continue

        # has no version file
        if not os.path.isfile(version_file):
            logger.warning(f'Package {name} does not have a version file! removed')
            shutil.rmtree(pkg_dir)
            continue

        with open(version_file, 'r') as f:
            version = f.read().strip()

        # wrong version
        target_version = all_packages[name]
        if version != target_version:
            logger.warning(f"Package {name} has inconsistent version! " +
                           f"Global is '{target_version}' while local is '{version}'. " +
                           f"removed")
            shutil.rmtree(pkg_dir)
            continue

        # existing package & correct version
        logger.debug(f'Existing: {name} {version}')
        packages[name] = version

    return packages

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
    pkg_dir = os.path.join(root, 'arch')
    os.makedirs(pkg_dir, exist_ok=True)

    all_packages = get_all_packages(arch_txt)
    existing_packages = get_existing_packages(all_packages, pkg_dir)

    missing_packages = [pkg for pkg in all_packages if pkg not in existing_packages]

    logger.info(f'All packages: {len(all_packages)}')
    logger.info(f'Existing packages: {len(existing_packages)}')
    logger.info(f'Missing: {len(missing_packages)}')

    seed = int(os.environ.get('RANDOM_SEED') or "20240202")
    logger.info(f"Random seed: {seed}")
    random.seed(seed)
    random.shuffle(missing_packages)

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
