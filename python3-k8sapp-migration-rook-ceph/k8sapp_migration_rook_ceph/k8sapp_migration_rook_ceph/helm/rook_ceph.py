#
# Copyright (c) 2021 Intel Corporation, Inc.
# Copyright (c) 2024 Wind River Systems, Inc.
#
# SPDX-License-Identifier: Apache-2.0
#

from k8sapp_migration_rook_ceph.common import constants as app_constants
from k8sapp_migration_rook_ceph.helm import storage
from sysinv.common import exception


class RookCephHelm(storage.StorageBaseHelm):
    """Class to encapsulate helm operations for the rook-operator chart"""
    CHART = app_constants.HELM_CHART_ROOK_CEPH
    HELM_RELEASE = app_constants.FLUXCD_HELMRELEASE_ROOK_CEPH

    def get_overrides(self, namespace=None):
        secrets = [{"name": "default-registry-key"}]
        overrides = {
            app_constants.HELM_NS_ROOK_CEPH: {
                'operator': self._get_operator_override(),
                'imagePullSecrets': secrets,
            }
        }

        if namespace in self.SUPPORTED_NAMESPACES:
            return overrides[namespace]
        elif namespace:
            raise exception.InvalidHelmNamespace(chart=self.CHART,
                                                 namespace=namespace)
        else:
            return overrides

    def _get_operator_override(self):
        operator = {
            'csi': {
                'enableRbdDriver': True
            },
            'enableFlexDriver': False,
            'logLevel': 'DEBUG',
        }
        return operator
