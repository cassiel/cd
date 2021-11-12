#1/bin/sh

rsync --progress --verbose --perms --times --recursive --delete \
      ~/SAMBA_VOLUME/MUSIC/.cddb/* \
      ~/CASSIEL/cd/abcde/.cddb/
git status
