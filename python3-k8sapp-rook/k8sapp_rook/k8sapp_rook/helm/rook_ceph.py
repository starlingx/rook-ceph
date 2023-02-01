#
# Copyright (c) 2018 Intel Corporation, Inc.
#
# SPDX-License-Identifier: Apache-2.0
#

from k8sapp_rook.common import constants as app_constants

import socket

from sysinv.common import constants
from sysinv.common import exception
from sysinv.common import utils as cutils

from sysinv.helm import base
from sysinv.helm import common


class RookCephHelm(base.BaseHelm):
    """Class to encapsulate helm operations for the rook-ceph chart"""

    CHART = app_constants.HELM_CHART_ROOK_CEPH
    SUPPORTED_NAMESPACES = base.BaseHelm.SUPPORTED_NAMESPACES + \
        [common.HELM_NS_STORAGE_PROVISIONER]
    SUPPORTED_APP_NAMESPACES = {
        constants.HELM_APP_ROOK_CEPH:
            base.BaseHelm.SUPPORTED_NAMESPACES + [common.HELM_NS_STORAGE_PROVISIONER],
    }

    def execute_manifest_updates(self, operator):
        # On application load this chart is enabled. Only disable if specified
        # by the user
        if not self._is_enabled(operator.APP, self.CHART,
                                common.HELM_NS_STORAGE_PROVISIONER):
            operator.chart_group_chart_delete(
                operator.CHART_GROUPS_LUT[self.CHART],
                operator.CHARTS_LUT[self.CHART])

    def get_namespaces(self):
        return self.SUPPORTED_NAMESPACES

    def get_overrides(self, namespace=None):
        overrides = {
            common.HELM_NS_STORAGE_PROVISIONER: {
                'cluster': self._get_cluster_override(),
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
