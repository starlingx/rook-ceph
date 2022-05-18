# Application tunables (maps to metadata)
%global app_name rook-ceph-apps
%global helm_repo stx-platform

# Install location
%global app_folder /usr/local/share/applications/helm

# Build variables
%global helm_folder /usr/lib/helm
#%global toolkit_version 0.1.0
%global rook_version 1.9.6

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

%package fluxcd
Summary: StarlingX K8s application for Rook Ceph FluxCD
Group: base
License: Apache-2.0

%description fluxcd
StarlingX K8s application for Rook Ceph FluxCD

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
%define app_tarball_armada %{app_name}-%{version}-%{tis_patch_ver}.tgz
%define app_tarball_fluxcd %{app_name}-fluxcd-%{version}-%{tis_patch_ver}.tgz

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

# package Armada
find . -type f ! -name '*.md5' -print0 | xargs -0 md5sum > checksum.md5
tar -zcf %{_builddir}/%{app_tarball_armada} -C %{app_staging}/ .

# package FluxCD
rm -f %{app_staging}/manifest.yaml

cd -
cp -R fluxcd-manifests %{app_staging}/
cd %{app_staging}

find . -type f ! -name '*.md5' -print0 | xargs -0 md5sum > checksum.md5
tar -zcf %{_builddir}/%{app_tarball_fluxcd} -C %{app_staging}/ .

cd -

# Cleanup staging
rm -fr %{app_staging}

%install
install -d -m 755 %{buildroot}/%{app_folder}
install -d -m 755 %{buildroot}%{_initrddir}
install -p -D -m 755 %{_builddir}/%{app_tarball_armada} %{buildroot}/%{app_folder}
install -m 750 %{SOURCE1} %{buildroot}%{_initrddir}/rook-mon-exit

install -p -D -m 755 %{_builddir}/%{app_tarball_fluxcd} %{buildroot}/%{app_folder}

%files
%defattr(-,root,root,-)
%{app_folder}/%{app_tarball_armada}
%{_initrddir}/rook-mon-exit

%files fluxcd
%defattr(-,root,root,-)
%{app_folder}/%{app_tarball_fluxcd}
