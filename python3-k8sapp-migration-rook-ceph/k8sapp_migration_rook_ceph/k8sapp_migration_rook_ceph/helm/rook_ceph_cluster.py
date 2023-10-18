
#
# Copyright (c) 2018 Intel Corporation, Inc.
# Copyright (c) 2024 Wind River Systems, Inc.
#
# SPDX-License-Identifier: Apache-2.0
#

from k8sapp_migration_rook_ceph.common import constants as app_constants
from k8sapp_migration_rook_ceph.helm import storage

import socket

from sysinv.common import constants
from sysinv.common import exception
from sysinv.common import utils as cutils


class RookCephClusterHelm(storage.StorageBaseHelm):
    """Class to encapsulate helm operations for the rook-ceph chart"""

    CHART = app_constants.HELM_CHART_ROOK_CEPH_CLUSTER
    HELM_RELEASE = app_constants.FLUXCD_HELMRELEASE_ROOK_CEPH_CLUSTER

    def get_overrides(self, namespace=None):
        overrides = {
            app_constants.HELM_NS_ROOK_CEPH: {
                'cephClusterSpec': self._get_cluster_override(),
                'cephFileSystems': self._get_cephfs_override(),
                'cephBlockPools': self._get_rdb_override(),
                'mds': self._get_mds_override(),
                'hook': self._get_hook_override(),
            }
        }

        if namespace in self.SUPPORTED_NAMESPACES:
            return overrides[namespace]
        elif namespace:
            raise exception.InvalidHelmNamespace(chart=self.CHART,
                                                 namespace=namespace)
        else:
            return overrides

    def _get_cephfs_override(self):
        if cutils.is_aio_simplex_system(self.dbapi):
            replica = 1
        else:
            replica = 2

        parameters = {
            'csi.storage.k8s.io/provisioner-secret-name': app_constants.ROOK_CEPH_FS_SECRET_NAME,
            'csi.storage.k8s.io/provisioner-secret-namespace': app_constants.ROOK_CEPH_CLUSTER_SECRET_NAMESPACE,
            'csi.storage.k8s.io/controller-expand-secret-name': app_constants.ROOK_CEPH_FS_SECRET_NAME,
            'csi.storage.k8s.io/controller-expand-secret-namespace': app_constants.ROOK_CEPH_CLUSTER_SECRET_NAMESPACE,
            'csi.storage.k8s.io/node-stage-secret-name': app_constants.ROOK_CEPH_FS_NODE_SECRET_NAME,
            'csi.storage.k8s.io/node-stage-secret-namespace': app_constants.ROOK_CEPH_CLUSTER_SECRET_NAMESPACE,
            'csi.storage.k8s.io/fstype': 'ext4'
        }

        storage_class = {
            'enabled': True,
            'name': app_constants.ROOK_CEPH_CLUSTER_CEPHFS_STORAGE_CLASS_NAME,
            'isDefault': False,
            'allowVolumeExpansion': True,
            'reclaimPolicy': 'Delete',
            'parameters': parameters
        }

        ceph_fs_config = [{
            'name': app_constants.ROOK_CEPH_CLUSTER_CEPHFS_FILE_SYSTEM_NAME,
            'spec': {
                'metadataPool': {
                    'replicated':
                        {'size': replica}},
                'metadataServer': {
                    'activeCount': 1,
                    'activeStandby': True},
                'dataPools': [{
                    'failureDomain': 'host',
                    'replicated':
                        {'size': replica}}],
            },
            'storageClass': storage_class
        }]

        return ceph_fs_config

    def _get_rdb_override(self):
        if cutils.is_aio_simplex_system(self.dbapi):
            replica = 1
        else:
            replica = 2

        parameters = {
            'imageFormat': '2',
            'imageFeatures': 'layering',
            'csi.storage.k8s.io/provisioner-secret-name': app_constants.ROOK_CEPH_RDB_SECRET_NAME,
            'csi.storage.k8s.io/provisioner-secret-namespace': app_constants.ROOK_CEPH_CLUSTER_SECRET_NAMESPACE,
            'csi.storage.k8s.io/controller-expand-secret-name': app_constants.ROOK_CEPH_RDB_SECRET_NAME,
            'csi.storage.k8s.io/controller-expand-secret-namespace': app_constants.ROOK_CEPH_CLUSTER_SECRET_NAMESPACE,
            'csi.storage.k8s.io/node-stage-secret-name': app_constants.ROOK_CEPH_RDB_NODE_SECRET_NAME,
            'csi.storage.k8s.io/node-stage-secret-namespace': app_constants.ROOK_CEPH_CLUSTER_SECRET_NAMESPACE,
            'csi.storage.k8s.io/fstype': 'ext4'
        }

        storage_class = {
            'enabled': True,
            'name': app_constants.ROOK_CEPH_CLUSTER_RDB_STORAGE_CLASS_NAME,
            'isDefault': True,
            'allowVolumeExpansion': True,
            'reclaimPolicy': 'Delete',
            'mountOptions': [],
            'parameters': parameters
        }

        rdb_config = [{
            'name': 'kube-rbd',
            'spec': {
                'failureDomain': 'host',
                'replicated': {'size': replica}
            },
            'storageClass': storage_class
        }]

        return rdb_config

    def _get_cluster_override(self):
        cluster = {
            'mon': {
                'count': self._get_mon_count(),
            },
        }

        return cluster

    def _get_mon_count(self):
        # change it with deployment configs:
        # AIO simplex/duplex have 1 mon, multi-node has 3 mons,
        # 2 controllers + first mon (and cannot reconfig)
        if cutils.is_aio_system(self.dbapi):
            return 1
        else:
            return 3

    def _get_mds_override(self):
        if cutils.is_aio_simplex_system(self.dbapi):
            replica = 1
        else:
            replica = 2

        mds = {
            'replica': replica,
        }

        return mds

    def _get_hook_override(self):
        hook = {
            'cleanup': {
                'mon_hosts': self._get_mon_hosts(),
            },
            'duplexPreparation': self._get_duplex_preparation(),
        }
        return hook

    def _get_mon_hosts(self):
        ceph_mon_label = "ceph-mon-placement=enabled"
        mon_hosts = []

        hosts = self.dbapi.ihost_get_list()
        for h in hosts:
            labels = self.dbapi.label_get_by_host(h.uuid)
            for label in labels:
                if (ceph_mon_label == str(label.label_key) + '=' + str(label.label_value)):
                    mon_hosts.append(h.hostname.encode('utf8', 'strict'))

        return mon_hosts

    def _get_duplex_preparation(self):
        duplex = {
            'enable': cutils.is_aio_duplex_system(self.dbapi)
        }

        if cutils.is_aio_duplex_system(self.dbapi):
            hosts = self.dbapi.ihost_get_by_personality(
                constants.CONTROLLER)
            for host in hosts:
                if host['hostname'] == socket.gethostname():
                    duplex.update({'activeController': host['hostname'].encode('utf8', 'strict')})

            pools = self.dbapi.address_pools_get_all()
            for pool in pools:
                if pool.name == 'management':
                    duplex.update({'floatIP': pool.floating_address})

        return duplex
