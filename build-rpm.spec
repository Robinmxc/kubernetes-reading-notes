#
# spec file for package kad
# Copyright (c) 2019 Ruijie. All Rights Reserved
#

Name:     kad
Version:  2.5.0
Release:  2021.08.26
Summary:  KAD RPM package
License:  GPLv2
Requires: ansible

%description
Kubernates auto deployment tool

%prep

%build

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
install -m 0750 /opt/kad/download.sh %{buildroot}/opt/kad/

%pre

%post
if [ ! -d "/opt/kad/workspace" ]; then
  cp -rpf /opt/kad/example/workspace /opt/kad/workspace
  chmod -R o-w /opt/kad/workspace
  chmod -R o-r /opt/kad/workspace
fi
if [ ! -f "/usr/bin/kad-play" ]; then
  link /opt/kad/kad-play.sh /usr/bin/kad-play
fi

%preun

%postun
if [ "$1" = "0" ] ; then
  if [ -f "/usr/bin/kad-play" ]; then
    rm -f /usr/bin/kad-play
  fi
fi

%files
%defattr(-,root,root,0664)
/opt/kad/
%attr(0770,root,root) /opt/kad/inventory/kad-workspace.py

%changelog
