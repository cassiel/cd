#1/bin/sh

# Assumes a working directory with an accumulated archive in .cddb - this sync merely copies
# it across to the Git repo.

rsync --progress --verbose --perms --times --recursive --delete \
      ~/SAMBA_VOLUME/MUSIC/.cddb/* \
      ~/CASSIEL/cd/abcde/.cddb/
git status
