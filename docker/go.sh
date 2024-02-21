#!/bin/bash

# ensure we are running in GitHub Actions
if [ "$GITHUB_ACTIONS" != "true" ]; then
    echo "This script is intended to run in GitHub Actions only. Exiting..."
    exit 1
fi

export TERM=xterm
echo "TERM=$TERM"

pwd
whoami

echo "TBT_UPDATE_PACKAGE=$TBT_UPDATE_PACKAGE"
echo "TBT_PACKAGE_NAME=$TBT_PACKAGE_NAME"
echo "TBT_PACKAGE_VERSION=$TBT_PACKAGE_VERSION"

if [ "$TBT_UPDATE_PACKAGE" != "true" ]; then
    echo "Amazing! No more packages to process! Exiting..."
    exit 0
fi

pacman -Sy >/dev/null
pacman -S --noconfirm --needed >/dev/null \
    aria2 wget curl \
    base-devel devtools \
    cloc jq

# set private key
if [ -z "$RANDOM_SSH_SECRET_KEY" ]; then
    echo "Error: RANDOM_SSH_SECRET_KEY is not set or empty. Exiting..."
    exit 1
else
    mkdir -p /root/.ssh && \
        echo "$RANDOM_SSH_SECRET_KEY" > /root/.ssh/id_ed25519 && \
        chmod 600 /root/.ssh/id_ed25519 && \
        ssh-keyscan gitlab.archlinux.org >> /root/.ssh/known_hosts
fi

TMP_DIR=/github/workspace/tmp_work_dir
RESULT_DIR=/github/workspace/arch/$TBT_PACKAGE_NAME
mkdir -p $TMP_DIR && cd $TMP_DIR && \
    echo pkgctl repo clone --switch $TBT_PACKAGE_VERSION $TBT_PACKAGE_NAME && \
    pkgctl repo clone --switch $TBT_PACKAGE_VERSION $TBT_PACKAGE_NAME && \
    chown -R nobody:nobody $TMP_DIR && \
    cd $TBT_PACKAGE_NAME \
    && \
    runuser -unobody -- makepkg --nodeps --noprepare --nobuild \
            --skippgpcheck --nocheck --noarchive \
    && \
    echo "Starting cloc" && \
    cloc --csv . > cloc.csv && \
    mkdir -p $RESULT_DIR && \
    echo $TBT_PACKAGE_VERSION > $RESULT_DIR/version && \
    mv cloc.csv $RESULT_DIR/

if [ $? -ne 0 ]; then
    echo "There were errors!"
    cd /github/workspace
    echo "$TBT_PACKAGE_NAME $TBT_PACKAGE_VERSION" >>arch.ignore

    # remove tmp dir regardless of what happens
    cd /github/workspace && rm -rf $TMP_DIR

    exit 1
fi

echo "Saving container metrics" && \
    sleep 10 && \
    /github/workspace/metrics/get-metrics | tee $RESULT_DIR/metrics.json

# remove tmp dir regardless of what happens
cd /github/workspace && rm -rf $TMP_DIR
