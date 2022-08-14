#!/usr/bin/env bash

#
# Creates database users for a local-only standalone setup of HeLO-Server
#

mongo admin \
  --host localhost \
  -u root \
  -p my_secure_password \
  --eval "db.createUser({user: 'helo', pwd: 'my_other_secure_password', roles: [{role: 'readWrite', db: 'helo'}]});"
