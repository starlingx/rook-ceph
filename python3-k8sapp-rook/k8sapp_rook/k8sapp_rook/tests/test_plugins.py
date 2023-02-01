#
# SPDX-License-Identifier: Apache-2.0
#

from sysinv.common import constants
from sysinv.tests.db import base as dbbase
from sysinv.tests.helm.test_helm import HelmOperatorTestSuiteMixin


class K8SAppRookAppMixin(object):
    app_name = constants.HELM_APP_ROOK_CEPH
    path_name = app_name + '.tgz'

    def setUp(self):
        super(K8SAppRookAppMixin, self).setUp()


# Test Configuration:
# - Controller
# - IPv6
class K8SAppRookControllerTestCase(K8SAppRookAppMixin,
                                   dbbase.BaseIPv6Mixin,
                                   HelmOperatorTestSuiteMixin,
                                   dbbase.ControllerHostTestCase):
    pass


# Test Configuration:
# - AIO
# - IPv4
class K8SAppRookAIOTestCase(K8SAppRookAppMixin,
                            HelmOperatorTestSuiteMixin,
                            dbbase.AIOSimplexHostTestCase):
    pass
