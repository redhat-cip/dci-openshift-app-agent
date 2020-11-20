Name:          dci-openshift-app-agent
Version:       0.0.VERS
Release:       1%{?dist}
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

install -p -D -m 644 hooks/pre-run.yml %{buildroot}%{_sysconfdir}/dci-openshift-app-agent/hooks/pre-run.yml
install -p -D -m 644 hooks/success.yml %{buildroot}%{_sysconfdir}/dci-openshift-app-agent/hooks/success.yml
install -p -D -m 644 hooks/user-tests.yml %{buildroot}%{_sysconfdir}/dci-openshift-app-agent/hooks/user-tests.yml
install -p -D -m 644 hooks/teardown.yml %{buildroot}%{_sysconfdir}/dci-openshift-app-agent/hooks/teardown.yml

install -p -D -m 644 dcirc.sh.dist %{buildroot}%{_sysconfdir}/dci-openshift-app-agent/dcirc.sh.dist
install -p -D -m 644 hosts.yml %{buildroot}%{_sysconfdir}/dci-openshift-app-agent/hosts.yml

install -p -D -m 644 sysconfig/dci-openshift-app-agent %{buildroot}%{_sysconfdir}/sysconfig/dci-openshift-app-agent

install -p -D -m 644 plays/configure.yml %{buildroot}%{_datadir}/dci-openshift-app-agent/plays/configure.yml
install -p -D -m 644 plays/failure.yml %{buildroot}%{_datadir}/dci-openshift-app-agent/plays/failure.yml
install -p -D -m 644 plays/upload_logs.yml %{buildroot}%{_datadir}/dci-openshift-app-agent/plays/upload_logs.yml
install -p -D -m 644 plays/dump_ocp_logs.yml %{buildroot}%{_datadir}/dci-openshift-app-agent/plays/dump_ocp_logs.yml
install -p -D -m 644 plays/check_prerequisite.yml %{buildroot}%{_datadir}/dci-openshift-app-agent/plays/check_prerequisite.yml
install -p -D -m 644 plays/pre-run.yml %{buildroot}%{_datadir}/dci-openshift-app-agent/plays/pre-run.yml
install -p -D -m 644 plays/running.yml %{buildroot}%{_datadir}/dci-openshift-app-agent/plays/running.yml
install -p -D -m 644 plays/dci-tests.yml %{buildroot}%{_datadir}/dci-openshift-app-agent/plays/dci-tests.yml

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
%config(noreplace) %{_sysconfdir}/dci-openshift-app-agent/hooks/pre-run.yml
%config(noreplace) %{_sysconfdir}/dci-openshift-app-agent/hooks/success.yml
%config(noreplace) %{_sysconfdir}/dci-openshift-app-agent/hooks/teardown.yml
%config(noreplace) %{_sysconfdir}/dci-openshift-app-agent/hooks/user-tests.yml

%config(noreplace) %{_sysconfdir}/dci-openshift-app-agent/hosts.yml

%config(noreplace) %{_sysconfdir}/sysconfig/dci-openshift-app-agent

%{_sysconfdir}/dci-openshift-app-agent/dcirc.sh.dist

%{_datadir}/dci-openshift-app-agent/ansible.cfg
%{_datadir}/dci-openshift-app-agent/dci-openshift-app-agent.yml
%{_datadir}/dci-openshift-app-agent/requirements.yml

%{_datadir}/dci-openshift-app-agent/plays/failure.yml
%{_datadir}/dci-openshift-app-agent/plays/check_prerequisite.yml
%{_datadir}/dci-openshift-app-agent/plays/configure.yml
%{_datadir}/dci-openshift-app-agent/plays/upload_logs.yml
%{_datadir}/dci-openshift-app-agent/plays/dump_ocp_logs.yml
%{_datadir}/dci-openshift-app-agent/plays/pre-run.yml
%{_datadir}/dci-openshift-app-agent/plays/running.yml
%{_datadir}/dci-openshift-app-agent/plays/dci-tests.yml

%{_datadir}/dci-openshift-app-agent/roles/get-logs-from-namespace/*

%{_datadir}/dci-openshift-app-agent/group_vars/all

%{_unitdir}/*

%exclude /%{_datadir}/dci-openshift-app-agent/*.pyc
%exclude /%{_datadir}/dci-openshift-app-agent/*.pyo

%dir %{_sharedstatedir}/dci-openshift-app-agent
%attr(0755, dci-openshift-app-agent, dci-openshift-app-agent) %{_sharedstatedir}/dci-openshift-app-agent
%{_sysconfdir}/sudoers.d/%{name}

%changelog
* Thu Nov 19 2020 Thomas Vassilian <tvassili@redhat.com> - 0.0.2
- Add role to dump all logs from pods in a namespace.
* Mon Jun 29 2020 Thomas Vassilian <tvassili@redhat.com> - 0.0.1
- Initial release.
