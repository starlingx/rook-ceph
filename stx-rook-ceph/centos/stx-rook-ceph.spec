# Application tunables (maps to metadata)
%global app_name rook-ceph-apps
%global helm_repo stx-platform

# Install location
%global app_folder /usr/local/share/applications/helm

# Build variables
%global helm_folder /usr/lib/helm
#%global toolkit_version 0.1.0
%global rook_version 1.2.7

Summary: StarlingX K8S application: Rook Ceph
Name: stx-rook-ceph
Version: 1.0
Release: %{tis_patch_ver}%{?_tis_dist}
License: Apache-2.0
Group: base
Packager: Intel
URL: unknown

Source0: %{name}-%{version}.tar.gz
Source1: rook-mon-exit.sh

BuildArch: noarch

BuildRequires: helm
BuildRequires: openstack-helm-infra
BuildRequires: chartmuseum
BuildRequires: python-k8sapp-rook
BuildRequires: python-k8sapp-rook-wheels

%description
The StarlingX K8S application for Rook Ceph

%prep
%setup

%build
# Host a server for the charts
chartmuseum --debug --port=8879 --context-path='/charts' --storage="local" --storage-local-rootdir="./helm-charts" &
sleep 2
helm repo add local http://localhost:8879/charts

# Make the charts. These produce a tgz file
cd helm-charts
make rook-operator
make rook-ceph
make rook-ceph-provisioner
cd -

# Terminate helm server (the last backgrounded task)
kill %1

# Create a chart tarball compliant with sysinv kube-app.py
%define app_staging %{_builddir}/staging
%define app_tarball %{app_name}-%{version}-%{tis_patch_ver}.tgz

# Setup staging
mkdir -p %{app_staging}
cp files/metadata.yaml %{app_staging}
cp manifests/manifest.yaml %{app_staging}
mkdir -p %{app_staging}/charts
cp helm-charts/*.tgz %{app_staging}/charts
cd %{app_staging}

# Populate metadata
sed -i 's/@APP_NAME@/%{app_name}/g' %{app_staging}/metadata.yaml
sed -i 's/@APP_VERSION@/%{version}-%{tis_patch_ver}/g' %{app_staging}/metadata.yaml
sed -i 's/@HELM_REPO@/%{helm_repo}/g' %{app_staging}/metadata.yaml

# Copy the plugins: installed in the buildroot
mkdir -p %{app_staging}/plugins
cp /plugins/%{app_name}/*.whl %{app_staging}/plugins

# package it up
find . -type f ! -name '*.md5' -print0 | xargs -0 md5sum > checksum.md5
tar -zcf %{_builddir}/%{app_tarball} -C %{app_staging}/ .

# Cleanup staging
rm -fr %{app_staging}

%install
install -d -m 755 %{buildroot}/%{app_folder}
install -d -m 755 %{buildroot}%{_initrddir}
install -p -D -m 755 %{_builddir}/%{app_tarball} %{buildroot}/%{app_folder}
install -m 750 %{SOURCE1} %{buildroot}%{_initrddir}/rook-mon-exit

%files
%defattr(-,root,root,-)
%{app_folder}/*
%{_initrddir}/rook-mon-exit
