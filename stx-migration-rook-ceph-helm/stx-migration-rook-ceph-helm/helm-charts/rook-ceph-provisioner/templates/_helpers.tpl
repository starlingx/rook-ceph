{{- define "script.osd_audit" -}}
#!/usr/bin/env python

import os
import subprocess

from kubernetes import __version__ as K8S_MODULE_VERSION
from kubernetes import config
from kubernetes import client
from kubernetes.client import Configuration
from kubernetes.client.rest import ApiException
from six.moves import http_client as httplib
from cephclient import wrapper

K8S_MODULE_MAJOR_VERSION = int(K8S_MODULE_VERSION.split('.')[0])

# Kubernetes Files
KUBERNETES_ADMIN_CONF = '/etc/kubernetes/admin.conf'

CEPH_MGR_PORT = 7999

def is_k8s_configured():
    """Check to see if the k8s admin config file exists."""
    if os.path.isfile(KUBERNETES_ADMIN_CONF):
        return True
    return False

class KubeOperator(object):

    def __init__(self):
        self._kube_client_batch = None
        self._kube_client_core = None
        self._kube_client_custom_objects = None

    def _load_kube_config(self):
        if not is_k8s_configured():
            raise exception.KubeNotConfigured()

        config.load_kube_config(KUBERNETES_ADMIN_CONF)
        if K8S_MODULE_MAJOR_VERSION < 12:
            c = Configuration()
        else:
            c = Configuration().get_default_copy()

        # Workaround: Turn off SSL/TLS verification
        c.verify_ssl = False
        Configuration.set_default(c)

    def _get_kubernetesclient_core(self):
        if not self._kube_client_core:
            self._load_kube_config()
            self._kube_client_core = client.CoreV1Api()
        return self._kube_client_core

    def _get_kubernetesclient_custom_objects(self):
        if not self._kube_client_custom_objects:
            self._load_kube_config()
            self._kube_client_custom_objects = client.CustomObjectsApi()
        return self._kube_client_custom_objects

    def kube_get_nodes(self):
        try:
            api_response = self._get_kubernetesclient_core().list_node()
            return api_response.items
        except ApiException as e:
            print("Kubernetes exception in kube_get_nodes: %s" % e)
            raise

    def kube_get_pods_by_selector(self, namespace, label_selector,
                                  field_selector):
        c = self._get_kubernetesclient_core()
        try:
            api_response = c.list_namespaced_pod(namespace,
                label_selector="%s" % label_selector,
                field_selector="%s" % field_selector)
            return api_response.items
        except ApiException as e:
            print("Kubernetes exception in "
                  "kube_get_pods_by_selector %s/%s/%s: %s",
                  namespace, label_selector, field_selector, e)

            return None

    def kube_delete_pod(self, name, namespace, **kwargs):
        body = {}

        if kwargs:
            body.update(kwargs)

        c = self._get_kubernetesclient_core()
        try:
            api_response = c.delete_namespaced_pod(name, namespace, body)
            return True
        except ApiException as e:
            if e.status == httplib.NOT_FOUND:
                print("Pod %s/%s not found." % (namespace, name))
                return False
            else:
                print("Failed to delete Pod %s/%s: " "%s" % (namespace, name, e.body))
                raise

    def get_custom_resource(self, group, version, namespace, plural, name):
        c = self._get_kubernetesclient_custom_objects()

        try:
            api_response = c.list_namespaced_custom_object(group, version, namespace,
                plural)
            return api_response
        except ApiException as ex:
            if ex.reason == "Not Found":
                print("Failed to delete custom object, Namespace %s: %s" % (namespace, str(ex.body).replace('\n', ' ')))
                pass

        return None

def osd_audit():
    kube = KubeOperator()
    group = "ceph.rook.io"
    version = "v1"
    namespace = "rook-ceph"
    plural = "cephclusters"
    name = "cephclusters.ceph.rook.io.ceph-cluster"

    try:
        ceph_api = wrapper.CephWrapper(endpoint='http://localhost:{}'.format(CEPH_MGR_PORT))
        response, body = ceph_api.health(body='text', timeout=30)
        if body == "HEALTH_OK":
            print("Cluster reports HEALTH_OK")
            return
        print(body)
    except IOError as e:
        print("Accessing Ceph API failed. Cluster health unknown. Proceeding.")
        pass

    cluster = {}
    try:
        cephcluster = kube.get_custom_resource(group, version, namespace, plural, name)
        if 'items' in cephcluster:
            cluster = cephcluster['items'][0]
    except ApiException as ex:
        if ex.reason == "Not Found":
            print("Failed to delete custom object, Namespace %s: %s" % (namespace, str(ex.body).replace('\n', ' ')))
            pass

    health = ""
    if cluster and cluster.has_key("status") and cluster["status"].has_key("ceph") and cluster['status']['ceph'].has_key("health"):
        health = cluster['status']['ceph']['health']
    else:
        print("Failed to get cluster['status']['ceph']['health']")
        return

    if health != "HEALTH_OK":
        delete_operator = False
        osd_nodes = cluster['spec']['storage']['nodes']
        nodes = {}

        node_list = kube.kube_get_nodes()
        for item in node_list:
            nodes[item.metadata.name] = item.spec.taints

        for n in osd_nodes:
            # get osd info declare in ceph cluster
            node_name = n['name']
            osd_devices = n['devices']

            # check whether there is osd pod running described in cephcluster osd_nodes
            label = "app=rook-ceph-osd,failure-domain=%s" % node_name
            pods = kube.kube_get_pods_by_selector(namespace, label, "")

            osd_pods = []
            for pod in pods:
                if pod.status.phase == 'Running':
                    osd_pods.append(pod)

            if len(osd_devices) != len(osd_pods) :
                # assume when osd pod number is not equal with this node osd device
                # operator should reset
                delete_operator = True

                # if osd pod is not running, as this node is tainted
                # unnecessary to delete operator pod
                taints = nodes[node_name]
                if taints:
                    for taint in taints:
                        if taint.key.startswith("node.kubernetes.io"):
                            # pod not running for taint
                            delete_operator[node_name] = False

            if delete_operator == True:
                break

        if delete_operator == True:
            operator_pod = kube.kube_get_pods_by_selector(namespace, "app=rook-ceph-operator", "")
            if operator_pod and operator_pod[0] and operator_pod[0].status.phase == 'Running':
                print("delete operator pod")
                kube.kube_delete_pod(operator_pod[0].metadata.name, namespace, grace_periods_seconds=0)


if __name__ == '__main__':
    osd_audit()
{{- end -}}
