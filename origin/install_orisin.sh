#!/usr/bin/env bash

sudo docker run -d --name "origin" \
    --privileged --net=host \
    -v /:/rootfs:ro -v /var/run:/var/run:rw -v /sys:/sys:ro -v /var/lib/docker:/var/lib/docker:rw \
    -v /var/lib/openshift/openshift.local.volumes:/var/lib/openshift/openshift.local.volumes \
    openshift/origin start
