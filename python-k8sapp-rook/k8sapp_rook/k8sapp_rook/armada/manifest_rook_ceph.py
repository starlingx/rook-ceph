# vim: tabstop=4 shiftwidth=4 softtabstop=4
#
# Copyright (c) 2020 Intel Corporation, Inc.
#
# SPDX-License-Identifier: Apache-2.0
#
# All Rights Reserved.
#

""" System inventory Armada manifest operator."""

from k8sapp_rook.helm.rook_ceph import RookCephHelm
from k8sapp_rook.helm.rook_ceph_provisioner import RookCephProvisionerHelm
from k8sapp_rook.helm.rook_operator import RookOperatorHelm

from sysinv.common import constants
from sysinv.helm import manifest_generic as generic


class RookCephArmadaManifestOperator(generic.GenericArmadaManifestOperator):

    APP = constants.HELM_APP_ROOK_CEPH
    ARMADA_MANIFEST = 'rook-ceph-manifest'

    CHART_GROUP_ROOK = 'starlingx-rook-charts'
    CHART_GROUPS_LUT = {
        RookOperatorHelm.CHART: CHART_GROUP_ROOK,
        RookCephHelm.CHART: CHART_GROUP_ROOK,
        RookCephProvisionerHelm: CHART_GROUP_ROOK,
    }

    CHARTS_LUT = {
        RookOperatorHelm.CHART: 'kube-system-rook-operator',
        RookCephHelm.CHART: 'kube-system-rook-ceph',
        RookCephProvisionerHelm.CHART: 'kube-system-rook-ceph-provisioner',
    }
