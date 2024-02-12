Name:          dci-openshift-app-agent
Version:       0.8.0
Release:       1.VERS%{?dist}
Summary:       DCI OpenShift App Agent
License:       ASL 2.0
URL:           https://github.com/redhat-cip/dci-openshift-app-agent
BuildArch:     noarch
Source0:       dci-openshift-app-agent-%{version}.tar.gz

BuildRequires: systemd
BuildRequires: systemd-units
Requires: sudo
Requires: dci-ansible >= 0.3.1
%if 0%{?rhel} && 0%{?rhel} < 8
Requires: python2-dciclient >= 3.1.0
%else
Requires: python3-dciclient >= 3.1.0
%endif
Requires: ansible-collection-redhatci-ocp >= 0.4.0
Requires(pre): shadow-utils
Requires(post): systemd
Requires(preun): systemd
Requires(postun): systemd

%description
DCI OpenShift App Agent

%prep
%setup -qc

%build

%clean

%install

make install BUILDROOT=%{buildroot} DATADIR=%{_datadir} NAME=%{name} SYSCONFDIR=%{_sysconfdir} BINDIR=%{_bindir} SHAREDSTATEDIR=%{_sharedstatedir} UNITDIR=%{_unitdir}

%pre
getent group dci-openshift-app-agent >/dev/null || groupadd -r dci-openshift-app-agent
getent passwd dci-openshift-app-agent >/dev/null || \
    useradd -m -g dci-openshift-app-agent -d %{_sharedstatedir}/dci-openshift-app-agent -s /bin/bash \
            -c "DCI Openshift App Agent service" dci-openshift-app-agent
exit 0

%post
%systemd_post %{name}.service
%systemd_preun %{name}.timer

%preun
%systemd_preun %{name}.service
%systemd_preun %{name}.timer

%postun
%systemd_postun %{name}.service
%systemd_postun %{name}.timer

%files
%license LICENSE
%config(noreplace) %{_sysconfdir}/dci-openshift-app-agent/hooks/*.yml
%config(noreplace) %{_sysconfdir}/dci-openshift-app-agent/hosts.yml
%config(noreplace) %{_sysconfdir}/dci-openshift-app-agent/settings.yml
%config(noreplace) %{_sysconfdir}/sysconfig/dci-openshift-app-agent

%{_bindir}/dci-openshift-app-agent-ctl

%{_sysconfdir}/dci-openshift-app-agent/dcirc.sh.dist

%{_datadir}/dci-openshift-app-agent/ansible.cfg
%{_datadir}/dci-openshift-app-agent/dci-openshift-app-agent.yml
%{_datadir}/dci-openshift-app-agent/plays/*.yml
%{_datadir}/dci-openshift-app-agent/plays/scripts/*
%{_datadir}/dci-openshift-app-agent/group_vars/all

%{_unitdir}/*

%dir %{_sharedstatedir}/dci-openshift-app-agent
%attr(0755, dci-openshift-app-agent, dci-openshift-app-agent) %{_sharedstatedir}/dci-openshift-app-agent
%{_sysconfdir}/sudoers.d/%{name}

%changelog
* Mon Feb 12 2024 Tony Garcia <tonyg@redhat.com> 0.8.0-1
- Move out dependencies to the redhatci.ocp collection

* Fri Jan 19 2024 Frederic Lepied <flepied@redhat.com> 0.7.2-1
- revert the requirment on redhatci.ocp >= 0.4.0 as the version
  doesn't exist

* Wed Jan 10 2024 Frederic Lepied <flepied@redhat.com> 0.7.1-1
- requires redhatci.ocp >= 0.4.0 for the deprecated_api_logs var

* Mon Oct 16 2023 Jorge A Gallegos <jgallego@redhat.com> - 0.7.0-2
- Depend on a version of collection with the right role names

* Fri Oct 13 2023 Tony Garcia <tonyg@redhat.com> 0.7.0-1
- Remove roles, use collections instead
- Does not require the dci-openshif-agent any more

* Mon Oct 09 2023 Jorge A Gallegos <jgallego@redhat.com> - 0.6.0-1
- Adding Red Hat CI OCP collection as a dependency

* Thu Oct  5 2023 Tony Garcia <tonyg@redhat.com> 0.5.11-1
- Requires dci-openshift-agent >= 0.5.12 for common-roles renaming

* Tue Sep 12 2023 Tony Garcia <tonyg@redhat.com> 0.5.10-1
- Bump requirements for dci-openshift-agent >= 0.5.10

* Thu Aug 31 2023 Tony Garcia <tonyg@redhat.com> 0.5.9-1
- Requires dci-openshift-agent >= 0.5.10 for utils

* Mon Jul 31 2023 Beto Rdz <josearod@redhat.com> 0.5.8-1
- Requires dci-openshift-agent >= 0.5.8 for common-roles

* Fri Apr 28 2023 Frederic Lepied <flepied@redhat.com> 0.5.5-1
- Requires dci-ansible >= 3.1.0 for the new component fields

* Mon Dec  5 2022 Frederic Lepied <flepied@redhat.com> 0.5.4-1
- requires doa >= 0.5.3 for new logic regarding rpm and git components

* Wed Nov  9 2022 Frederic Lepied <flepied@redhat.com> 0.5.3-1
- bump the requires for python-dciclient to >= 2.6.0 to get dci-diff-jobs

* Thu Sep 22 2022 Frederic Lepied <flepied@redhat.com> 0.5.2-1
- use make install
- remove requires on ansible-role-dci-cvp

* Mon Jun  6 2022 Tony Garcia <tonyg@redhat.com> 0.5.1-1
- Remove requirements.yml

* Thu Mar 24 2022 Frederic Lepied <flepied@redhat.com> 0.5.0-1
- use dci-vault-client

* Wed Mar  9 2022 Frederic Lepied <flepied@redhat.com> 0.4.0-1
- add a Requires on dci-openshift-agent >= 0.4.0 to access the common roles

* Fri Jan 28 2022 Tony Garcia <tonyg@redhat.com> 0.3.2-1
- Add LICENSE file

* Sun Oct 10 2021 Ramon Perez <raperez@redhat.com> 0.3.1-1
- Sub-ids support in d-o-a-a user. Including d-o-a-a/plays/scripts/ entry.

* Wed May  5 2021 Frederic Lepied <flepied@redhat.com> 0.3.0-1
- add dci-openshift-app-agent-ctl and settings.yml

* Thu Apr 22 2021 Frederic Lepied <flepied@redhat.com> 0.2.1-1
- Include all roles

* Mon Jan 11 2021 Tony Garcia <tonyg@redhat.com> - 0.1.1-1
- Add package and repo info for jobs

* Mon Dec 21 2020 Frederic Lepied <flepied@redhat.com> 0.1.0-1
- refactor

* Thu Nov 19 2020 Thomas Vassilian <tvassili@redhat.com> - 0.0.2
- Add role to dump all logs from pods in a namespace.

* Mon Jun 29 2020 Thomas Vassilian <tvassili@redhat.com> - 0.0.1
- Initial release.
