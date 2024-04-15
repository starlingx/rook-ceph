# rook-ceph
Rook-ceph migration fluxCD app

####  Top Level Directory Structure
```bash
├── rook-ceph    # Root Folder
│   ├── bindep.txt
│   ├── debian_build_layer.cfg
│   ├── debian_iso_image.inc
│   ├── debian_pkg_dirs
│   ├── migration-rook-ceph-helm              # importing of upstream rook-ceph helm packages
│   ├── python3-k8sapp-migration-rook-ceph    # lifecycle managemnt code to support flux apps
│   ├── README.md
│   ├── requirements.txt
│   ├── stx-migration-rook-ceph-helm      # helm Package manager for the app
│   ├── test-requirements.txt
│   └── tox.ini
```

### About rook-ceph migration
Rook is a Ceph orchestrator providing a containerized solution for Ceph Storage. This application targets compatibility with Ceph Nautilus using the last rook-ceph version (v1.7.11) available that has official support for it. For newer versions of ceph and rook-ceph, there's a [rook ceph app](https://opendev.org/starlingx/app-rook-ceph) available.

### Installation Guide
For instructions on how to build and install migration rook-ceph, follow the [StarlingX Rook Ceph Migration App installation guide](https://wiki.openstack.org/wiki/StarlingX/Containers/Applications/rook-ceph-migration).


#### References
[StarlingX](https://www.starlingx.io/)

[Rook Ceph](https://rook.io/)

[Rook Ceph 1.7 Documentation](https://rook.io/docs/rook/v1.7/)

[Rook Ceph App](https://opendev.org/starlingx/app-rook-ceph)
