#
# spec file for package kad
# Copyright (c) 2019 Ruijie. All Rights Reserved
#

Name:     kad
Version:  1.0.0
Release:  1
Summary:  KAD RPM package
License:  GPLv2
Requires: ansible

%description
Kubernates auto deployment tool

%prep

%build
unzip -oq /opt/kad/down/sourceid-kad-r1.5.1.zip -d /tmp/sourceid-kad-debug
touch /tmp/sourceid-kad-debug/images-download.ok

%install
mkdir -p %{buildroot}/opt/kad/
mkdir -p %{buildroot}/opt/kad/down
mkdir -p %{buildroot}/opt/kad/bin
mkdir -p %{buildroot}/opt/kad/temp
cp -rpf /opt/kad/roles %{buildroot}/opt/kad/roles
cp -rpf /opt/kad/playbooks %{buildroot}/opt/kad/playbooks
cp -rpf /opt/kad/inventory %{buildroot}/opt/kad/inventory
cp -rpf /opt/kad/manifests %{buildroot}/opt/kad/manifests
cp -rpf /opt/kad/example %{buildroot}/opt/kad/example
cp -rpf /opt/kad/tools %{buildroot}/opt/kad/tools
install -m 0644 /opt/kad/ansible.cfg %{buildroot}/opt/kad/
install -m 0644 /opt/kad/meta-info.yml %{buildroot}/opt/kad/
install -m 0750 /opt/kad/kad-play.sh %{buildroot}/opt/kad/
install -m 0750 /opt/kad/sourceid-setup.sh %{buildroot}/opt/kad/
install -m 0644 /opt/kad/down/sourceid-kad-r1.5.1.zip %{buildroot}/opt/kad/down/
cp -rpf /tmp/sourceid-kad-debug %{buildroot}/opt/kad/down/sourceid-kad-debug

%pre

%post
if [ ! -d "/opt/kad/workspace" ]; then
  cp -rpf /opt/kad/example/workspace /opt/kad/workspace
fi
if [ ! -f "/usr/bin/kad-play" ]; then
  link /opt/kad/kad-play.sh /usr/bin/kad-play
fi

%preun
if [ -f "/usr/bin/kad-play" ]; then
  rm -f /usr/bin/kad-play
fi

%postun

%files
%defattr(-,root,root,0644)
/opt/kad/
%attr(0755,root,root) /opt/kad/inventory/kad-workspace.py

%changelog
