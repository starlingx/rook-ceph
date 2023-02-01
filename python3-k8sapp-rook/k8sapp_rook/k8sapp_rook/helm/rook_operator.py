#
# Copyright (c) 2021 Intel Corporation, Inc.
#
# SPDX-License-Identifier: Apache-2.0
#

from k8sapp_rook.common import constants as app_constants

from sysinv.common import constants
from sysinv.common import exception

from sysinv.helm import base
from sysinv.helm import common


class RookOperatorHelm(base.BaseHelm):
    """Class to encapsulate helm operations for the rook-operator chart"""

    CHART = app_constants.HELM_CHART_ROOK_OPERATOR
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
        secrets = [{"name": "default-registry-key"}]

        overrides = {
            common.HELM_NS_STORAGE_PROVISIONER: {
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
