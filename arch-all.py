import os
import requests
import json
import shutil

import config

from config import logging
logger = logging.getLogger('arch-all')

def request_json(url):
    response = requests.get(url)
    assert response.status_code == 200, \
        f"Failed to retrieve data. Status code: {response.status_code}"
    data = response.json()
    return data

def get_all_packages(num_pages):
    packages = {}
    for page in range(1, num_pages + 1):
        print(f"Page {page}: ", end='')
        url = f"https://archlinux.org/packages/search/json/?sort=name&page={page}"
        data = request_json(url)
        print(f"{len(data['results'])}")
        for pkg in data['results']:
            name = pkg['pkgbase']
            version = f"{pkg['pkgver']}-{pkg['pkgrel']}"
            epoch = pkg['epoch']
            if epoch != 0:
                version = f'{epoch}:{version}'
            repo = pkg['repo']
            if repo not in ['core', 'extra', 'multilib']:
                continue
            packages[name] = version
    return packages

def remove_old_packages(all_packages, pkg_root_dir):
    for name in os.listdir(pkg_root_dir):
        pkg_dir = os.path.join(pkg_root_dir, name)
        version_file = os.path.join(pkg_dir, 'version')
        metrics_file = os.path.join(pkg_dir, 'metrics.json')

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

        with open(metrics_file, 'r') as f:
            try:
                _ = json.load(f)
            except json.JSONDecodeError:
                logger.warning(f'Package {name} has invalid metrics file! removed')
                shutil.rmtree(pkg_dir)
                continue
    return

if __name__ == "__main__":
    root_page = request_json("https://archlinux.org/packages/search/json/?sort=name")
    num_pages = root_page['num_pages']
    logger.info(f"There are {num_pages} pages")

    all_packages = get_all_packages(num_pages)
    logger.info(f"All packages: {len(all_packages)}")

    root = config.CURRENT_DIR
    arch_txt = os.path.join(root, 'arch.txt')
    pkg_dir = os.path.join(root, 'arch')

    # save to arch.txt
    with open(arch_txt, 'w') as f:
        for name in sorted(all_packages.keys()):
            version = all_packages[name]
            f.write(f'{name} {version}\n')

    os.makedirs(pkg_dir, exist_ok=True)
    remove_old_packages(all_packages, pkg_dir)
