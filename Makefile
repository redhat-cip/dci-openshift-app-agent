NAME = dci-openshift-app-agent
BUILDROOT =
DATADIR = /usr/share
SYSCONFDIR = /etc
BINDIR = /usr/bin
SHAREDSTATEDIR = /var/lib
UNITDIR = /usr/lib/systemd/system


install:
	install -p -D -m 644 ansible.cfg $(BUILDROOT)$(DATADIR)/dci-openshift-app-agent/ansible.cfg
	install -p -D -m 644 dci-openshift-app-agent.yml  $(BUILDROOT)$(DATADIR)/dci-openshift-app-agent/dci-openshift-app-agent.yml

	for hook in hooks/*.yml; do \
	  install -p -D -m 644 $$hook  $(BUILDROOT)$(SYSCONFDIR)/dci-openshift-app-agent/$$hook; \
	done

	install -p -D -m 644 dcirc.sh.dist $(BUILDROOT)$(SYSCONFDIR)/dci-openshift-app-agent/dcirc.sh.dist
	install -p -D -m 644 hosts.yml $(BUILDROOT)$(SYSCONFDIR)/dci-openshift-app-agent/hosts.yml
	install -p -D -m 644 settings.yml $(BUILDROOT)$(SYSCONFDIR)/dci-openshift-app-agent/settings.yml

	install -p -D -m 644 sysconfig/dci-openshift-app-agent $(BUILDROOT)$(SYSCONFDIR)/sysconfig/dci-openshift-app-agent

	for play in plays/*.yml; do \
	  install -p -D -m 644 $$play $(BUILDROOT)$(DATADIR)/dci-openshift-app-agent/$$play; \
	done

	for script in plays/scripts/*; do \
	  install -p -D -m 755 $$script $(BUILDROOT)$(DATADIR)/dci-openshift-app-agent/$$script; \
	done

	install -p -D -m 644 group_vars/all $(BUILDROOT)$(DATADIR)/dci-openshift-app-agent/group_vars/all

	install -p -D -m 644 systemd/$(NAME).service $(BUILDROOT)$(UNITDIR)/$(NAME).service
	install -p -D -m 644 systemd/$(NAME).timer $(BUILDROOT)$(UNITDIR)/$(NAME).timer

	install -p -D -m 440 dci-openshift-app-agent.sudo $(BUILDROOT)$(SYSCONFDIR)/sudoers.d/$(NAME)
	install -p -d -m 755 $(BUILDROOT)/$(SHAREDSTATEDIR)/$(NAME)
	find samples -type f -exec install -v -p -D -m 644 "{}" "$(BUILDROOT)$(SHAREDSTATEDIR)/dci-openshift-app-agent/{}" \;
	find roles/* -type f -exec install -v -p -D -m 644 "{}" "$(BUILDROOT)$(DATADIR)/dci-openshift-app-agent/{}" \;

	install -v -p -D -m 755 dci-openshift-app-agent-ctl $(BUILDROOT)$(BINDIR)/dci-openshift-app-agent-ctl
