#
# Copyright (c) 2018 Wind River Systems, Inc.
# Copyright (c) 2024 Wind River Systems, Inc.
#
# SPDX-License-Identifier: Apache-2.0
#

from k8sapp_migration_rook_ceph.common import constants as app_constants
from k8sapp_migration_rook_ceph.helm import storage

from kubernetes.client.rest import ApiException
from oslo_log import log as logging
from sysinv.common import constants
from sysinv.common import exception
from sysinv.common import kubernetes
from sysinv.common import utils

LOG = logging.getLogger(__name__)


class RookCephClusterProvisionerHelm(storage.StorageBaseHelm):
    """Class to encapsulate helm operations for the rook-ceph-provisioner chart"""

    CHART = app_constants.HELM_CHART_ROOK_CEPH_PROVISIONER
    HELM_RELEASE = app_constants.FLUXCD_HELMRELEASE_ROOK_CEPH_PROVISIONER

    def get_overrides(self, namespace=None):
        base_name = 'ceph-pool'
        secret_name = base_name + '-' + constants.CEPH_POOL_KUBE_NAME

        if utils.is_aio_simplex_system(self.dbapi):
            replica = 1
        else:
            replica = 2

        audit = utils.is_aio_duplex_system(self.dbapi)

        overrides = {
            app_constants.HELM_NS_ROOK_CEPH: {
                "global": {
                    "job_ceph_mon_audit": audit,
                },
                "provisionStorage": {
                    "defaultStorageClass": constants.K8S_RBD_PROV_STOR_CLASS_NAME,
                    "classdefaults": {
                        "monitors": self._get_monitors(),
                        "adminId": constants.K8S_RBD_PROV_USER_NAME,
                        "adminSecretName": constants.K8S_RBD_PROV_ADMIN_SECRET_NAME,
                    },
                    "classes": {
                        "name": constants.K8S_RBD_PROV_STOR_CLASS_NAME,
                        "pool": {
                            "pool_name": constants.CEPH_POOL_KUBE_NAME,
                            "replication": replica,
                            "crush_rule_name": "storage_tier_ruleset",
                            "chunk_size": 64,
                        },
                        "secret": {
                            "userId": constants.CEPH_POOL_KUBE_NAME,
                            "userSecretName": secret_name,
                        }
                    },
                },
                "host_provision": {
                    "controller_hosts": self._get_controller_hosts(),
                },
                "ceph_audit_jobs": self._get_ceph_audit(),
            }
        }

        if namespace in self.SUPPORTED_NAMESPACES:
            return overrides[namespace]
        elif namespace:
            raise exception.InvalidHelmNamespace(chart=self.CHART,
                                                 namespace=namespace)
        else:
            return overrides

    def _get_rook_mon_ip(self):
        try:
            kube = kubernetes.KubeOperator()
            mon_ip_name = 'rook-ceph-mon-endpoints'

            configmap = kube.kube_read_config_map(mon_ip_name,
                                                  app_constants.HELM_NS_ROOK_CEPH)
            if configmap is not None:
                data = configmap.data['data']
                LOG.info('rook configmap data is %s' % data)
                mons = data.split(',')
                lists = []
                for mon in mons:
                    mon = mon.split('=')
                    lists.append(mon[1])
                ip_str = ','.join(lists)
                LOG.info('rook mon ip is %s' % ip_str)
                return ip_str

        except Exception as e:
            LOG.error("Kubernetes exception in rook mon ip: %s" % e)
            raise
        return ''

    def _is_rook_ceph(self):
        try:
            label = "mon_cluster=" + app_constants.HELM_NS_ROOK_CEPH
            kube = kubernetes.KubeOperator()
            pods = kube.kube_get_pods_by_selector(app_constants.HELM_NS_ROOK_CEPH, label, "")
            if len(pods) > 0:
                return True
        except ApiException as ae:
            LOG.error("get monitor pod exception: %s" % ae)
        except exception.SysinvException as se:
            LOG.error("get sysinv exception: %s" % se)

        return False

    def _get_monitors(self):
        if self._is_rook_ceph():
            return self._get_rook_mon_ip()
        else:
            return ''

    def _get_controller_hosts(self):
        controller_hosts = []

        hosts = self.dbapi.ihost_get_by_personality(constants.CONTROLLER)
        for h in hosts:
            controller_hosts.append(h.hostname.encode('utf8', 'strict'))

        return controller_hosts

    def _get_ceph_audit(self):
        audit = {}

        if utils.is_aio_duplex_system(self.dbapi):
            pools = self.dbapi.address_pools_get_all()
            for pool in pools:
                if pool.name == 'management':
                    audit.update({'floatIP': pool.floating_address})

        return audit
