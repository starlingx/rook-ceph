#
# Copyright (c) 2021 Intel Corporation, Inc.
#
# SPDX-License-Identifier: Apache-2.0
#
# All Rights Reserved.
#

""" System inventory App lifecycle operator."""
# Temporary disable pylint for lifecycle hooks
# This will be reverted in a future commit
# pylint: disable=no-member
# pylint: disable=no-name-in-module
from oslo_log import log as logging
from sysinv.common import constants
from sysinv.common import exception
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
        # Rbd
        if hook_info.lifecycle_type == constants.APP_LIFECYCLE_TYPE_RBD:
            if hook_info.operation == constants.APP_APPLY_OP and \
                    hook_info.relative_timing == constants.APP_LIFECYCLE_TIMING_PRE:
                return lifecycle_utils.create_rbd_provisioner_secrets(app_op, app, hook_info)
            elif hook_info.operation == constants.APP_REMOVE_OP and \
                    hook_info.relative_timing == constants.APP_LIFECYCLE_TIMING_POST:
                return lifecycle_utils.delete_rbd_provisioner_secrets(app_op, app, hook_info)

        # Resources
        elif hook_info.lifecycle_type == constants.APP_LIFECYCLE_TYPE_RESOURCE:
            if hook_info.operation == constants.APP_APPLY_OP and \
                    hook_info.relative_timing == constants.APP_LIFECYCLE_TIMING_PRE:
                return lifecycle_utils.create_local_registry_secrets(app_op, app, hook_info)
            elif hook_info.operation == constants.APP_REMOVE_OP and \
                    hook_info.relative_timing == constants.APP_LIFECYCLE_TIMING_POST:
                return lifecycle_utils.delete_local_registry_secrets(app_op, app, hook_info)

        # Operation
        elif hook_info.lifecycle_type == constants.APP_LIFECYCLE_TYPE_OPERATION:
            if hook_info.operation == constants.APP_APPLY_OP and \
                    hook_info.relative_timing == constants.APP_LIFECYCLE_TIMING_POST:
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
