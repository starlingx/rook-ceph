

Other values

---

## .operator.csi:

CSI CephFS plugin daemonset update strategy, supported values are OnDelete and RollingUpdate.
Default value is RollingUpdate.
```
rbdPluginUpdateStrategy: OnDelete
```

CSI Rbd plugin daemonset update strategy, supported values are OnDelete and RollingUpdate.
Default value is RollingUpdate.
```
cephFSPluginUpdateStrategy: OnDelete
```

Set provisonerTolerations and provisionerNodeAffinity for provisioner pod.
The CSI provisioner would be best to start on the same nodes as other ceph daemons.
```
provisionerTolerations:
  - key: key
    operator: Exists
    effect: NoSchedule
provisionerNodeAffinity: key1=value1,value2; key2=value3
```

Set pluginTolerations and pluginNodeAffinity for plugin daemonset pods.
The CSI plugins need to be started on all the nodes where the clients need to mount the storage.
```
pluginTolerations:
  - key: key
    operator: Exists
    effect: NoSchedule
pluginNodeAffinity: key1=value1,value2; key2=value3
cephfsGrpcMetricsPort: 9091
cephfsLivenessMetricsPort: 9081
rbdGrpcMetricsPort: 9090
```

Enable Ceph Kernel clients on kernel < 4.17. If your kernel does not support quotas for CephFS
you may want to disable this setting. However, this will cause an issue during upgrades
with the FUSE client. See the upgrade guide: https://rook.io/docs/rook/v1.2/ceph-upgrade.html
```
forceCephFSKernelClient: true
rbdLivenessMetricsPort: 9080
```

## .operator:

if true, run rook operator on the host network
```
useOperatorHostNetwork: true
```

Rook Agent configuration
toleration: NoSchedule, PreferNoSchedule or NoExecute
tolerationKey: Set this to the specific key of the taint to tolerate
tolerations: Array of tolerations in YAML format which will be added to agent deployment
nodeAffinity: Set to labels of the node to match
flexVolumeDirPath: The path where the Rook agent discovers the flex volume plugins
libModulesDirPath: The path where the Rook agent can find kernel modules
```
agent:
  toleration: NoSchedule
  tolerationKey: key
  tolerations:
  - key: key
    operator: Exists
    effect: NoSchedule
  nodeAffinity: key1=value1,value2; key2=value3
  mountSecurityMode: Any
```

For information on FlexVolume path, please refer to https://rook.io/docs/rook/master/flexvolume.html
```
flexVolumeDirPath: /usr/libexec/kubernetes/kubelet-plugins/volume/exec/
libModulesDirPath: /lib/modules
mounts: mount1=/host/path:/container/path,/host/path2:/container/path2
```

Rook Discover configuration
toleration: NoSchedule, PreferNoSchedule or NoExecute
tolerationKey: Set this to the specific key of the taint to tolerate
tolerations: Array of tolerations in YAML format which will be added to agent deployment
nodeAffinity: Set to labels of the node to match
```
discover:
  toleration: NoSchedule
  tolerationKey: key
  tolerations:
  - key: key
    operator: Exists
    effect: NoSchedule
  nodeAffinity: key1=value1,value2; key2=value3
```

In some situations SELinux relabelling breaks (times out) on large filesystems, and doesn't work with cephfs ReadWriteMany volumes (last relabel wins).
Disable it here if you have similar issues.
For more details see https://github.com/rook/rook/issues/2417
```
enableSelinuxRelabeling: true
```

Writing to the hostPath is required for the Ceph mon and osd pods. Given the restricted permissions in OpenShift with SELinux,
the pod must be running privileged in order to write to the hostPath volume, this must be set to true then.
```
hostpathRequiresPrivileged: false
```

Disable automatic orchestration when new devices are discovered.
```
disableDeviceHotplug: false
```

Blacklist certain disks according to the regex provided.
```
discoverDaemonUdev:
```
