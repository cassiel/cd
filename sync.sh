#1/bin/sh

rsync --progress --verbose --perms --times --recursive --delete \
      ~/MACOS_VOLUME/MUSIC/.cddb/* \
      ~/CASSIEL/cd/abcde/.cddb/
