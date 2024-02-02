#!/bin/bash

# ensure we are running in GitHub Actions
if [ "$GITHUB_ACTIONS" != "true" ]; then
    echo "This script is intended to run in GitHub Actions only. Exiting..."
    exit 1
fi

pacman -Sy
pacman -S --noconfirm --needed >/dev/null \
    aria2 wget curl \
    base-devel devtools \
    cloc

# set private key
if [ -z "$RANDOM_SSH_SECRET_KEY" ]; then
    echo "Error: RANDOM_SSH_SECRET_KEY is not set or empty. Exiting..."
    exit 1
fi

HOME=/root
SSH_DIR=$HOME/.ssh
PRIVATE_KEY=$SSH_DIR/id_ed25519

mkdir -p $SSH_DIR && \
    echo "$RANDOM_SSH_SECRET_KEY" > $PRIVATE_KEY && \
    chmod 600 $PRIVATE_KEY

# add public key to known hosts
ssh-keyscan gitlab.archlinux.org  >> ~/.ssh/known_hosts
# # test connection
# ssh -vvvv -T git@gitlab.archlinux.org

WORKSPACE_ROOT=/github/workspace
PKG_ROOT=$WORKSPACE_ROOT/pkg
CLOC_RESULT=$WORKSPACE_ROOT/cloc.sqlite

cat <<EndsHERE >$CLOC_RESULT
create table metadata (          -- github.com/AlDanial/cloc v 1.98
                timestamp varchar(500),
                Project   varchar(500),
                elapsed_s real);
create table t        (
                Project       varchar(500)   ,
                Language      varchar(500)   ,
                File          varchar(500)   ,
                File_dirname  varchar(500)   ,
                File_basename varchar(500)   ,
                nBlank        integer        ,
                nComment      integer        ,
                nCode         integer        ,
                nScaled       real           );
EndsHERE

# clone all packages
echo "thebesttv: Cloning all arch packages ..."
mkdir -p $PKG_ROOT && cd $PKG_ROOT && \
    pkgctl repo clone --universe 2>/dev/null | grep '==> Cloning'
echo "thebesttv: Cloning complete!"
# change permisison
chown -R nobody:nobody $PKG_ROOT

# start collect cloc stat
cd $PKG_ROOT
# iterate over all dirs
for pkg in */; do
    # remove trailing "/"
    pkg="${pkg%/}"

    cd $PKG_ROOT/$pkg
    runuser -unobody -- makepkg --nodeps --noprepare --nobuild \
            --skippgpcheck --nocheck --noarchive
    cloc \
        --sql=$CLOC_RESULT \
        --sql-append \
        --sql-project=$pkg \
        .

    cd $PKG_ROOT
    rm -rf $pkg
done

cd $WORKSPACE_ROOT
sqlite3 cloc.db <$CLOC_RESULT
