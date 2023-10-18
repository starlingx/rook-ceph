#!/bin/bash
#
# Copyright (c) 2020 Intel Corporation, Inc.
# Copyright (c) 2024 Wind River Systems, Inc.
#
# SPDX-License-Identifier: Apache-2.0
#

RETVAL=0

################################################################################
# Start Action
################################################################################
function start {
    return
}

################################################################################
# Stop Action
################################################################################
function stop {
    pgrep ceph-mon
    if [ x"$?" = x"0" ]; then
        kubectl --kubeconfig=/etc/kubernetes/admin.conf delete        \
                deployments.apps -n rook-ceph rook-ceph-mon-a
        kubectl --kubeconfig=/etc/kubernetes/admin.conf delete po     \
                -n rook-ceph --selector="app=rook-ceph-mon,mon=a"
    fi

    pgrep ceph-osd
    if [ x"$?" = x"0" ]; then
        kubectl --kubeconfig=/etc/kubernetes/admin.conf delete        \
                deployments.apps -n rook-ceph                         \
                --selector="app=rook-ceph-osd,failure-domain=$(hostname)"
        kubectl --kubeconfig=/etc/kubernetes/admin.conf delete po     \
                --selector="app=rook-ceph-osd,failure-domain=$(hostname)" \
                -n rook-ceph
    fi
}

################################################################################
# Status Action
################################################################################
function status {
    pgrep sysinv-api

    RETVAL=$?

    return
}

################################################################################
# Main Entry
################################################################################

case "$1" in
    start)
        start
        ;;

    stop)
        stop
        ;;

    restart)
        stop
        start
        ;;

    status)
        status
        ;;

    *)
        echo "usage: $0 { start | stop | status | restart }"
        exit 1
        ;;
esac

exit $RETVAL
