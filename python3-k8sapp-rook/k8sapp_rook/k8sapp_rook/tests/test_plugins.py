#
# SPDX-License-Identifier: Apache-2.0
#

from sysinv.common import constants
from sysinv.tests.db import base as dbbase


class K8SAppRookAppMixin(object):
    app_name = constants.HELM_APP_ROOK_CEPH
    path_name = app_name + '.tgz'

    def setUp(self):  # pylint: disable=useless-super-delegation
        super(K8SAppRookAppMixin, self).setUp()

    def test_stub(self):
        # This unit test stub should be removed when real
        # unit tests are added
        pass


# Test Configuration:
# - Controller
# - IPv6
class K8SAppRookControllerTestCase(K8SAppRookAppMixin,
                                   dbbase.BaseIPv6Mixin,
                                   dbbase.ControllerHostTestCase):
    pass


# Test Configuration:
# - AIO
# - IPv4
class K8SAppRookAIOTestCase(K8SAppRookAppMixin,
                            dbbase.AIOSimplexHostTestCase):
    pass
