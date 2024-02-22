#!/bin/python

import os
import sys
import json

all_packages = {}

# list all dirs under arch/
for dir in os.listdir('arch'):
    # list all files under arch/$dir
    with open(f'arch/{dir}/metrics.json') as f:
        packages = json.load(f)
        all_packages[dir] = packages

def get_sum(all_packages, key):
    return sum([data[key] for data in all_packages.values()])

def to_GB(bytes):
    return bytes / 1024 / 1024 / 1024

print(f'Receive: {to_GB(get_sum(all_packages, "receive")):.2f} GB')
print(f'Transmit: {to_GB(get_sum(all_packages, "transmit")):.2f} GB')
print(f'Disk: {to_GB(get_sum(all_packages, "disk")):.2f} GB')
