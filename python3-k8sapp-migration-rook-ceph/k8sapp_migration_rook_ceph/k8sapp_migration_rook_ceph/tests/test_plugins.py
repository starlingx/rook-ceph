#
# Copyright (c) 2024 Wind River Systems, Inc.
#
# SPDX-License-Identifier: Apache-2.0
#

from k8sapp_migration_rook_ceph.common import constants as app_constants
from sysinv.tests.db import base as dbbase


class K8SAppMigrationRookAppMixin(object):
    app_name = app_constants.HELM_APP_ROOK_CEPH
    path_name = app_name + '.tgz'

    def setUp(self):  # pylint: disable=useless-super-delegation
        super(K8SAppMigrationRookAppMixin, self).setUp()


# Test Configuration:
# - Controller
# - IPv6
class K8SAppMigrationRookControllerTestCase(K8SAppMigrationRookAppMixin,
                                   dbbase.BaseIPv6Mixin,
                                   dbbase.ControllerHostTestCase):
    pass


# Test Configuration:
# - AIO
# - IPv4
class K8SAppMigrationRookAIOTestCase(K8SAppMigrationRookAppMixin,
                            dbbase.AIOSimplexHostTestCase):
    pass
