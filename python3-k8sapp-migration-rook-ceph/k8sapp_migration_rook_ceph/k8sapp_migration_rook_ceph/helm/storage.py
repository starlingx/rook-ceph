#
# Copyright (c) 2024 Wind River Systems, Inc.
#
# SPDX-License-Identifier: Apache-2.0
#

from sysinv.helm import base
from k8sapp_migration_rook_ceph.common import constants as app_constants


class BaseHelm(base.FluxCDBaseHelm):
    """Class to encapsulate storage related service operations for helm"""

    SUPPORTED_NAMESPACES = base.BaseHelm.SUPPORTED_NAMESPACES + \
        [app_constants.HELM_NS_ROOK_CEPH]
    SUPPORTED_APP_NAMESPACES = {
        app_constants.HELM_APP_ROOK_CEPH: SUPPORTED_NAMESPACES,
    }


class StorageBaseHelm(BaseHelm):
    """Class to encapsulate storage service operations for helm"""

    def _is_enabled(self, app_name, chart_name, namespace):
        """
        Check if the chart is enable at a system level

        :param app_name: Application name
        :param chart_name: Chart supplied with the application
        :param namespace: Namespace where the chart will be executed

        Returns true by default if an exception occurs as most charts are
        enabled.
        """
        return super(StorageBaseHelm, self)._is_enabled(
            app_name, chart_name, namespace)

    def execute_kustomize_updates(self, operator):
        """
        Update the elements of FluxCD kustomize manifests.

        This allows a helm chart plugin to use the FluxCDKustomizeOperator to
        make dynamic structural changes to the application manifest based on the
        current conditions in the platform

        Changes currenty include updates to the top level kustomize manifest to
        disable helm releases.

        :param operator: an instance of the FluxCDKustomizeOperator
        """
        if not self._is_enabled(operator.APP, self.CHART,
                                app_constants.HELM_NS_ROOK_CEPH):
            operator.helm_release_resource_delete(self.HELM_RELEASE)
