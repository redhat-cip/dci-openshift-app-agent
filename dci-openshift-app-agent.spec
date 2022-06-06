Name:          dci-openshift-app-agent
Version:       0.5.1
Release:       1.VERS%{?dist}
Summary:       DCI OpenShift App Agent
License:       ASL 2.0
URL:           https://github.com/redhat-cip/dci-openshift-app-agent
BuildArch:     noarch
Source0:       dci-openshift-app-agent-%{version}.tar.gz

BuildRequires: systemd
BuildRequires: systemd-units
Requires: sudo
Requires: dci-openshift-agent >= 0.4.0
Requires: dci-ansible
%if 0%{?rhel} && 0%{?rhel} < 8
Requires: python2-dciclient >= 2.3.0
%else
Requires: python3-dciclient >= 2.3.0
%endif
Requires: ansible-role-dci-cvp
Requires: ansible-collection-community-kubernetes
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
install -p -D -m 644 ansible.cfg %{buildroot}%{_datadir}/dci-openshift-app-agent/ansible.cfg
install -p -D -m 644 dci-openshift-app-agent.yml  %{buildroot}%{_datadir}/dci-openshift-app-agent/dci-openshift-app-agent.yml

for hook in hooks/*.yml; do
    install -p -D -m 644 $hook  %{buildroot}%{_sysconfdir}/dci-openshift-app-agent/$hook
done

install -p -D -m 644 dcirc.sh.dist %{buildroot}%{_sysconfdir}/dci-openshift-app-agent/dcirc.sh.dist
install -p -D -m 644 hosts.yml %{buildroot}%{_sysconfdir}/dci-openshift-app-agent/hosts.yml
install -p -D -m 644 settings.yml %{buildroot}%{_sysconfdir}/dci-openshift-app-agent/settings.yml

install -p -D -m 644 sysconfig/dci-openshift-app-agent %{buildroot}%{_sysconfdir}/sysconfig/dci-openshift-app-agent

for play in plays/*.yml; do
    install -p -D -m 644 $play %{buildroot}%{_datadir}/dci-openshift-app-agent/$play
done

for script in plays/scripts/*; do
    install -p -D -m 755 $script %{buildroot}%{_datadir}/dci-openshift-app-agent/$script
done

install -p -D -m 644 group_vars/all %{buildroot}%{_datadir}/dci-openshift-app-agent/group_vars/all

install -p -D -m 644 systemd/%{name}.service %{buildroot}%{_unitdir}/%{name}.service
install -p -D -m 644 systemd/%{name}.timer %{buildroot}%{_unitdir}/%{name}.timer

install -p -D -m 440 dci-openshift-app-agent.sudo %{buildroot}%{_sysconfdir}/sudoers.d/%{name}
install -p -d -m 755 %{buildroot}/%{_sharedstatedir}/%{name}
find samples -type f -exec install -v -p -D -m 644 "{}" "%{buildroot}%{_sharedstatedir}/dci-openshift-app-agent/{}" \;
find roles/* -type f -exec install -v -p -D -m 644 "{}" "%{buildroot}%{_datadir}/dci-openshift-app-agent/{}" \;

install -v -p -D -m 755 dci-openshift-app-agent-ctl %{buildroot}%{_bindir}/dci-openshift-app-agent-ctl

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
%{_datadir}/dci-openshift-app-agent/roles/*
%{_datadir}/dci-openshift-app-agent/group_vars/all

%{_unitdir}/*

%dir %{_sharedstatedir}/dci-openshift-app-agent
%attr(0755, dci-openshift-app-agent, dci-openshift-app-agent) %{_sharedstatedir}/dci-openshift-app-agent
%{_sysconfdir}/sudoers.d/%{name}

%changelog
* Mon Jun  6 2022 Tony Garcia <tonyg@redhat.com> 0.5.1-1
- Remove requirements.yml

* Thu Mar 24 2022 Frederic Lepied <flepied@redhat.com> 0.5.0-1
- use dci-vault-client

* Wed Mar  9 2022 Frederic Lepied <flepied@redhat.com> 0.4.0-1
- add a Requires on dci-openshift-agent >= 0.4.0 to access the common roles

* Fri Jan 28 2022 Tony Garcia <tonyg@redhat.com> 0.3.2-1
- Add LICENSE file

* Wed Oct 10 2021 Ramon Perez <raperez@redhat.com> 0.3.1-1
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
