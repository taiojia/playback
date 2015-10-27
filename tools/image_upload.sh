#!/usr/bin/env bash

source ~/admin-openrc.sh
glance image-create --name "ubuntu1404" --is-public true --disk-format qcow2 \
          --container-format bare \
          --file $1
