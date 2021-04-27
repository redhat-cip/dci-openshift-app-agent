Name:          dci-openshift-app-agent
Version:       0.1.1
Release:       1.VERS%{?dist}
Summary:       DCI Openshift App Agent
License:       ASL 2.0
URL:           https://github.com/redhat-cip/dci-openshift-app-agent
BuildArch:     noarch
Source0:       dci-openshift-app-agent-%{version}.tar.gz

BuildRequires: systemd
BuildRequires: systemd-units
Requires: sudo
Requires: dci-ansible
Requires: ansible-role-dci-import-keys
Requires: ansible-role-dci-retrieve-component
Requires: ansible-role-dci-cvp
Requires(pre): shadow-utils
Requires(post): systemd
Requires(preun): systemd
Requires(postun): systemd

%description
DCI Openshift App Agent

%prep
%setup -qc

%build

%clean

%install
install -p -D -m 644 ansible.cfg %{buildroot}%{_datadir}/dci-openshift-app-agent/ansible.cfg
install -p -D -m 644 dci-openshift-app-agent.yml  %{buildroot}%{_datadir}/dci-openshift-app-agent/dci-openshift-app-agent.yml
install -p -D -m 644 requirements.yml  %{buildroot}%{_datadir}/dci-openshift-app-agent/requirements.yml

for hook in hooks/*.yml; do
    install -p -D -m 644 $hook  %{buildroot}%{_sysconfdir}/dci-openshift-app-agent/$hook
done

install -p -D -m 644 dcirc.sh.dist %{buildroot}%{_sysconfdir}/dci-openshift-app-agent/dcirc.sh.dist
install -p -D -m 644 hosts.yml %{buildroot}%{_sysconfdir}/dci-openshift-app-agent/hosts.yml

install -p -D -m 644 sysconfig/dci-openshift-app-agent %{buildroot}%{_sysconfdir}/sysconfig/dci-openshift-app-agent

for play in plays/*.yml; do
    install -p -D -m 644 $play %{buildroot}%{_datadir}/dci-openshift-app-agent/$play
done

install -p -D -m 644 group_vars/all %{buildroot}%{_datadir}/dci-openshift-app-agent/group_vars/all

install -p -D -m 644 systemd/%{name}.service %{buildroot}%{_unitdir}/%{name}.service
install -p -D -m 644 systemd/%{name}.timer %{buildroot}%{_unitdir}/%{name}.timer

install -p -D -m 440 dci-openshift-app-agent.sudo %{buildroot}%{_sysconfdir}/sudoers.d/%{name}
install -p -d -m 755 %{buildroot}/%{_sharedstatedir}/%{name}
find samples -type f -exec install -Dm 755 "{}" "%{buildroot}%{_sharedstatedir}/dci-openshift-app-agent/{}" \;
find roles/get-logs-from-namespace -type f -exec install -v -p -D -m 644 "{}" "%{buildroot}%{_datadir}/dci-openshift-app-agent/{}" \;


%pre
getent group dci-openshift-app-agent >/dev/null || groupadd -r dci-openshift-app-agent
getent passwd dci-openshift-app-agent >/dev/null || \
    useradd -r -m -g dci-openshift-app-agent -d %{_sharedstatedir}/dci-openshift-app-agent -s /bin/bash \
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
%config(noreplace) %{_sysconfdir}/dci-openshift-app-agent/hooks/*.yml

%config(noreplace) %{_sysconfdir}/dci-openshift-app-agent/hosts.yml

%config(noreplace) %{_sysconfdir}/sysconfig/dci-openshift-app-agent

%{_sysconfdir}/dci-openshift-app-agent/dcirc.sh.dist

%{_datadir}/dci-openshift-app-agent/ansible.cfg
%{_datadir}/dci-openshift-app-agent/dci-openshift-app-agent.yml
%{_datadir}/dci-openshift-app-agent/requirements.yml

%{_datadir}/dci-openshift-app-agent/plays/*.yml

%{_datadir}/dci-openshift-app-agent/roles/get-logs-from-namespace/*

%{_datadir}/dci-openshift-app-agent/group_vars/all

%{_unitdir}/*

%exclude /%{_datadir}/dci-openshift-app-agent/*.pyc
%exclude /%{_datadir}/dci-openshift-app-agent/*.pyo

%dir %{_sharedstatedir}/dci-openshift-app-agent
%attr(0755, dci-openshift-app-agent, dci-openshift-app-agent) %{_sharedstatedir}/dci-openshift-app-agent
%{_sysconfdir}/sudoers.d/%{name}

%changelog
* Mon Jan 11 16:56:36 CST 2021 Tony Garcia <tonyg@redhat.com> - 0.1.1-1
- Add package and repo info for jobs

* Mon Dec 21 2020 Frederic Lepied <flepied@redhat.com> 0.1.0-1
- refactor

* Thu Nov 19 2020 Thomas Vassilian <tvassili@redhat.com> - 0.0.2
- Add role to dump all logs from pods in a namespace.

* Mon Jun 29 2020 Thomas Vassilian <tvassili@redhat.com> - 0.0.1
- Initial release.
