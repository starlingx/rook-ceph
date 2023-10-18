# Copyright (c) 2024 Wind River Systems, Inc.
#
# SPDX-License-Identifier: Apache-2.0
#
from k8sapp_migration_rook_ceph.common import constants as app_constants
from k8sapp_migration_rook_ceph.tests import test_plugins

from sysinv.db import api as dbapi

from sysinv.tests.db import base as dbbase
from sysinv.tests.db import utils as dbutils
from sysinv.tests.helm import base


class RookTestCase(test_plugins.K8SAppMigrationRookAppMixin,
                   base.HelmTestCaseMixin):

    def setUp(self):
        super(RookTestCase, self).setUp()
        self.app = dbutils.create_test_app(name=app_constants.HELM_APP_ROOK_CEPH)
        self.dbapi = dbapi.get_instance()


class RookIPv4ControllerHostTestCase(RookTestCase,
                                     dbbase.ProvisionedControllerHostTestCase):

    def test_rook_ceph_overrides(self):
        d_overrides = self.operator.get_helm_chart_overrides(
            app_constants.HELM_CHART_ROOK_CEPH,
            cnamespace=app_constants.HELM_NS_ROOK_CEPH)
        self.assertOverridesParameters(d_overrides, {
            'operator': {
                'csi': {
                    'enableRbdDriver': True
                },
                'enableFlexDriver': False,
                'logLevel': 'DEBUG'},
            'imagePullSecrets': [
                {'name': 'default-registry-key'}
            ]
        })

    def test_rook_ceph_cluster_overrides(self):
        e_overrides = self.operator.get_helm_chart_overrides(
            app_constants.HELM_CHART_ROOK_CEPH_CLUSTER,
            cnamespace=app_constants.HELM_NS_ROOK_CEPH)

        self.assertOverridesParameters(e_overrides, {
            'cephClusterSpec': {
                'mon': {
                    'count': 3
                }
            },
            'cephFileSystems':
            [
                {
                    'name': 'kube-cephfs',
                    'spec':
                    {
                        'metadataPool': {'replicated': {'size': 2}},
                        'metadataServer': {'activeCount': 1, 'activeStandby': True},
                        'dataPools':
                        [{'failureDomain': 'host', 'replicated': {'size': 2}}],
                    },
                    'storageClass':
                    {
                        'enabled': True,
                        'name': 'cephfs',
                        'isDefault': False,
                        'allowVolumeExpansion': True,
                        'reclaimPolicy': 'Delete',
                        'parameters':
                        {
                            'csi.storage.k8s.io/provisioner-secret-name': 'rook-csi-cephfs-provisioner',
                            'csi.storage.k8s.io/provisioner-secret-namespace': 'rook-ceph',
                            'csi.storage.k8s.io/controller-expand-secret-name': 'rook-csi-cephfs-provisioner',
                            'csi.storage.k8s.io/controller-expand-secret-namespace': 'rook-ceph',
                            'csi.storage.k8s.io/node-stage-secret-name': 'rook-csi-cephfs-node',
                            'csi.storage.k8s.io/node-stage-secret-namespace': 'rook-ceph',
                            'csi.storage.k8s.io/fstype': 'ext4',
                        },
                    },
                },
            ],
            'cephBlockPools':
            [
                {
                    'name': 'kube-rbd',
                    'spec': {'failureDomain': 'host', 'replicated': {'size': 2}},
                    'storageClass':
                    {
                        'enabled': True,
                        'name': 'general',
                        'isDefault': True,
                        'allowVolumeExpansion': True,
                        'reclaimPolicy': 'Delete',
                        'mountOptions': [],
                        'parameters':
                        {
                            'imageFormat': '2',
                            'imageFeatures': 'layering',
                            'csi.storage.k8s.io/provisioner-secret-name': 'rook-csi-rbd-provisioner',
                            'csi.storage.k8s.io/provisioner-secret-namespace': 'rook-ceph',
                            'csi.storage.k8s.io/controller-expand-secret-name': 'rook-csi-rbd-provisioner',
                            'csi.storage.k8s.io/controller-expand-secret-namespace': 'rook-ceph',
                            'csi.storage.k8s.io/node-stage-secret-name': 'rook-csi-rbd-node',
                            'csi.storage.k8s.io/node-stage-secret-namespace': 'rook-ceph',
                            'csi.storage.k8s.io/fstype': 'ext4',
                        },
                    },
                },
            ],
            'mds': {'replica': 2},
            'hook':
            {
                'cleanup': {'mon_hosts': []},
                'duplexPreparation': {'enable': False}
            }
        })

    def test_rook_ceph_provisioner_overrides(self):
        f_overrides = self.operator.get_helm_chart_overrides(
            app_constants.HELM_CHART_ROOK_CEPH_PROVISIONER,
            cnamespace=app_constants.HELM_NS_ROOK_CEPH)

        self.assertOverridesParameters(f_overrides, {
            'global': {'job_ceph_mon_audit': False},
            'provisionStorage':
            {
                'defaultStorageClass': 'general',
                'classdefaults':
                    {'monitors': '', 'adminId': 'admin', 'adminSecretName': 'ceph-admin'},
                'classes':
                {
                    'name': 'general',
                    'pool':
                    {
                        'pool_name': 'kube-rbd',
                        'replication': 2,
                        'crush_rule_name': 'storage_tier_ruleset',
                        'chunk_size': 64,
                    },
                    'secret':
                        {'userId': 'kube-rbd', 'userSecretName': 'ceph-pool-kube-rbd'}, },
            },
            'host_provision': {'controller_hosts': [b'controller-0']},
            'ceph_audit_jobs': {},
        })


class RookIPv6AIODuplexSystemTestCase(RookTestCase,
                                      dbbase.BaseIPv6Mixin,
                                      dbbase.ProvisionedAIODuplexSystemTestCase):

    def test_rook_ceph_overrides(self):
        a_overrides = self.operator.get_helm_chart_overrides(
            app_constants.HELM_CHART_ROOK_CEPH,
            cnamespace=app_constants.HELM_NS_ROOK_CEPH)

        self.assertOverridesParameters(a_overrides, {
            'operator':
            {
                'csi': {'enableRbdDriver': True},
                'enableFlexDriver': False,
                'logLevel': 'DEBUG',
            },
            'imagePullSecrets': [{'name': 'default-registry-key'}],
        })

    def test_rook_ceph_cluster_overrides(self):
        b_overrides = self.operator.get_helm_chart_overrides(
            app_constants.HELM_CHART_ROOK_CEPH_CLUSTER,
            cnamespace=app_constants.HELM_NS_ROOK_CEPH)

        self.assertOverridesParameters(b_overrides, {
            'cephClusterSpec': {'mon': {'count': 1}},
            'cephFileSystems':
            [
                {
                    'name': 'kube-cephfs',
                    'spec':
                    {
                        'metadataPool': {'replicated': {'size': 2}},
                        'metadataServer': {'activeCount': 1, 'activeStandby': True},
                        'dataPools':
                        [{'failureDomain': 'host', 'replicated': {'size': 2}}],
                    },
                    'storageClass':
                    {
                        'enabled': True,
                        'name': 'cephfs',
                        'isDefault': False,
                        'allowVolumeExpansion': True,
                        'reclaimPolicy': 'Delete',
                        'parameters':
                        {
                            'csi.storage.k8s.io/provisioner-secret-name': 'rook-csi-cephfs-provisioner',
                            'csi.storage.k8s.io/provisioner-secret-namespace': 'rook-ceph',
                            'csi.storage.k8s.io/controller-expand-secret-name': 'rook-csi-cephfs-provisioner',
                            'csi.storage.k8s.io/controller-expand-secret-namespace': 'rook-ceph',
                            'csi.storage.k8s.io/node-stage-secret-name': 'rook-csi-cephfs-node',
                            'csi.storage.k8s.io/node-stage-secret-namespace': 'rook-ceph',
                            'csi.storage.k8s.io/fstype': 'ext4',
                        },
                    },
                },
            ],
            'cephBlockPools':
            [
                {
                    'name': 'kube-rbd',
                    'spec': {'failureDomain': 'host', 'replicated': {'size': 2}},
                    'storageClass':
                    {
                        'enabled': True,
                        'name': 'general',
                        'isDefault': True,
                        'allowVolumeExpansion': True,
                        'reclaimPolicy': 'Delete',
                        'mountOptions': [],
                        'parameters':
                        {
                            'imageFormat': '2',
                            'imageFeatures': 'layering',
                            'csi.storage.k8s.io/provisioner-secret-name': 'rook-csi-rbd-provisioner',
                            'csi.storage.k8s.io/provisioner-secret-namespace': 'rook-ceph',
                            'csi.storage.k8s.io/controller-expand-secret-name': 'rook-csi-rbd-provisioner',
                            'csi.storage.k8s.io/controller-expand-secret-namespace': 'rook-ceph',
                            'csi.storage.k8s.io/node-stage-secret-name': 'rook-csi-rbd-node',
                            'csi.storage.k8s.io/node-stage-secret-namespace': 'rook-ceph',
                            'csi.storage.k8s.io/fstype': 'ext4',
                        },
                    },
                },
            ],
            'mds': {'replica': 2},
            'hook':
            {
                'cleanup': {'mon_hosts': []},
                'duplexPreparation': {'enable': True, 'floatIP': 'fd01::2'},
            },
        })

    def test_rook_ceph_provisioner_overrides(self):
        c_overrides = self.operator.get_helm_chart_overrides(
            app_constants.HELM_CHART_ROOK_CEPH_PROVISIONER,
            cnamespace=app_constants.HELM_NS_ROOK_CEPH)

        self.assertOverridesParameters(c_overrides, {
            'global': {'job_ceph_mon_audit': True},
            'provisionStorage':
            {
                'defaultStorageClass': 'general',
                'classdefaults':
                    {'monitors': '', 'adminId': 'admin', 'adminSecretName': 'ceph-admin'},
                'classes':
                {
                    'name': 'general',
                    'pool':
                    {
                        'pool_name': 'kube-rbd',
                        'replication': 2,
                        'crush_rule_name': 'storage_tier_ruleset',
                        'chunk_size': 64,
                    },
                    'secret':
                    {
                        'userId': 'kube-rbd',
                        'userSecretName': 'ceph-pool-kube-rbd'
                    }, },
            },
            'host_provision': {'controller_hosts': [b'controller-0', b'controller-1']},
            'ceph_audit_jobs': {'floatIP': 'fd01::2'},
        })
