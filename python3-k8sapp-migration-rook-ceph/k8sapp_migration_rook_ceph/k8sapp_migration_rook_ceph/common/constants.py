#
# Copyright (c) 2020 Intel Corporation, Inc.
# Copyright (c) 2024 Wind River Systems, Inc.
#
# SPDX-License-Identifier: Apache-2.0
#

# Application Name
HELM_NS_ROOK_CEPH = 'rook-ceph'
HELM_APP_ROOK_CEPH = 'rook-ceph-migration'

# Helm: Supported charts:
# These values match the names in the chart package's Chart.yaml
HELM_CHART_ROOK_CEPH = 'rook-ceph'
HELM_CHART_ROOK_CEPH_CLUSTER = 'rook-ceph-cluster'
HELM_CHART_ROOK_CEPH_PROVISIONER = 'rook-ceph-provisioner'

# FluxCD
FLUXCD_HELMRELEASE_ROOK_CEPH = 'rook-ceph'
FLUXCD_HELMRELEASE_ROOK_CEPH_CLUSTER = 'rook-ceph-cluster'
FLUXCD_HELMRELEASE_ROOK_CEPH_PROVISIONER = 'rook-ceph-provisioner'

ROOK_CEPH_CLUSTER_SECRET_NAMESPACE = 'rook-ceph'

ROOK_CEPH_RDB_SECRET_NAME = 'rook-csi-rbd-provisioner'
ROOK_CEPH_RDB_NODE_SECRET_NAME = 'rook-csi-rbd-node'

ROOK_CEPH_FS_SECRET_NAME = 'rook-csi-cephfs-provisioner'
ROOK_CEPH_FS_NODE_SECRET_NAME = 'rook-csi-cephfs-node'

ROOK_CEPH_CLUSTER_RDB_STORAGE_CLASS_NAME = 'general'
ROOK_CEPH_CLUSTER_CEPHFS_STORAGE_CLASS_NAME = 'cephfs'

ROOK_CEPH_CLUSTER_CEPHFS_FILE_SYSTEM_NAME = 'kube-cephfs'
