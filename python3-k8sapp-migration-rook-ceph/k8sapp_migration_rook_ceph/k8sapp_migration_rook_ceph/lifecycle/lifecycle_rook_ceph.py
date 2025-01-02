#
# Copyright (c) 2021 Intel Corporation, Inc.
# Copyright (c) 2024 Wind River Systems, Inc.
#
# SPDX-License-Identifier: Apache-2.0
#
# All Rights Reserved.
#

""" System inventory App lifecycle operator."""

from oslo_log import log as logging
from sysinv.common import constants
from sysinv.common import exception
from sysinv.common import kubernetes
from sysinv.common import utils as cutils
from sysinv.helm import lifecycle_base as base
from sysinv.helm.lifecycle_constants import LifecycleConstants
from sysinv.helm import lifecycle_utils as lifecycle_utils

LOG = logging.getLogger(__name__)


class RookCephAppLifecycleOperator(base.AppLifecycleOperator):
    def app_lifecycle_actions(self, context, conductor_obj, app_op, app, hook_info):
        """ Perform lifecycle actions for an operation

        :param context: request context
        :param conductor_obj: conductor object
        :param app_op: AppOperator object
        :param app: AppOperator.Application object
        :param hook_info: LifecycleHookInfo object

        """
        # Fluxcd request
        if hook_info.lifecycle_type == LifecycleConstants.APP_LIFECYCLE_TYPE_FLUXCD_REQUEST:
            if (hook_info.operation == constants.APP_REMOVE_OP and
                      hook_info.relative_timing == LifecycleConstants.APP_LIFECYCLE_TIMING_PRE):
                return self.remove_finalizers_crd()

        # Resources
        if hook_info.lifecycle_type == LifecycleConstants.APP_LIFECYCLE_TYPE_RESOURCE:
            if hook_info.operation == constants.APP_APPLY_OP:
                if hook_info.relative_timing == LifecycleConstants.APP_LIFECYCLE_TIMING_PRE:
                    return lifecycle_utils.create_local_registry_secrets(app_op, app, hook_info)
            elif (hook_info.operation == constants.APP_REMOVE_OP and
                      hook_info.relative_timing == LifecycleConstants.APP_LIFECYCLE_TIMING_POST):
                return lifecycle_utils.delete_local_registry_secrets(app_op, app, hook_info)

        # Operation
        elif hook_info.lifecycle_type == LifecycleConstants.APP_LIFECYCLE_TYPE_OPERATION:
            if (hook_info.operation == constants.APP_APPLY_OP and
                    hook_info.relative_timing == LifecycleConstants.APP_LIFECYCLE_TIMING_POST):
                return self.post_apply(context, conductor_obj, app, hook_info)

        # Use the default behaviour for other hooks
        super(RookCephAppLifecycleOperator, self).app_lifecycle_actions(context, conductor_obj, app_op, app, hook_info)

    def post_apply(self, context, conductor_obj, app, hook_info):
        """ Post apply actions

        :param context: request context
        :param conductor_obj: conductor object
        :param app: AppOperator.Application object
        :param hook_info: LifecycleHookInfo object

        """
        if LifecycleConstants.EXTRA not in hook_info:
            raise exception.LifecycleMissingInfo("Missing {}".format(LifecycleConstants.EXTRA))
        if LifecycleConstants.APP_APPLIED not in hook_info[LifecycleConstants.EXTRA]:
            raise exception.LifecycleMissingInfo(
                "Missing {} {}".format(LifecycleConstants.EXTRA, LifecycleConstants.APP_APPLIED))

        if hook_info[LifecycleConstants.EXTRA][LifecycleConstants.APP_APPLIED]:
            # apply any runtime configurations that are needed for
            # rook_ceph application
            conductor_obj._update_config_for_rook_ceph(context)

    def remove_finalizers_crd(self):
        """ Remove finalizers from CustomResourceDefinitions (CRDs)

        This function removes finalizers from rook-ceph CRDs for application removal
        operation

        """
        # Get all CRDs related to rook-ceph
        cmd_crds = ["kubectl", "--kubeconfig", kubernetes.KUBERNETES_ADMIN_CONF, "get", "crd",
                    "-o=jsonpath='{.items[?(@.spec.group==\"ceph.rook.io\")].metadata.name}'"]

        stdout, stderr = cutils.trycmd(*cmd_crds)
        if not stderr:
            crds = stdout.replace("'", "").strip().split(" ")
            for crd_name in crds:
                # Get custom resources based on each rook-ceph CRD
                cmd_instances = ["kubectl", "--kubeconfig", kubernetes.KUBERNETES_ADMIN_CONF,
                                 "get", "-n", "rook-ceph", crd_name, "-o", "name"]
                stdout, stderr = cutils.trycmd(*cmd_instances)
                crd_instances = stdout.strip().split("\n")
                if not stderr and crd_instances:
                    for crd_instance in crd_instances:
                        if crd_instance:
                            # Patch each custom resource to remove finalizers
                            patch_cmd = ["kubectl", "--kubeconfig", kubernetes.KUBERNETES_ADMIN_CONF,
                                         "patch", "-n", "rook-ceph", crd_instance, "-p",
                                         "{\"metadata\":{\"finalizers\":null}}", "--type=merge"]
                            stdout, stderr = cutils.trycmd(*patch_cmd)
                            LOG.debug("{} \n stdout: {} \n stderr: {}".format(crd_instance, stdout, stderr))
        else:
            LOG.error("Error removing finalizers: {stderr}")
