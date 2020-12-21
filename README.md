# DCI Openshift App Agent

`dci-openshift-app-agent` enables Cloud-Native Applications and Operators in Red Hat Distributed CI service.

## Table of Contents

- [Requirements](#requirements)
- [Workflow](#workflow)
- [Tags](#tags)
- [License](#license)
- [Contact](#contact)

## Requirements

## Worflow

The `dci-openshift-app-agent` is an Ansible playbook that enables Cloud-Native Applications and Operators in Red Hat Distributed CI service. The main entrypoint is the file “dci-openshift-app-agent.yml”. It is composed of several steps executed sequentially.

In case of a failure (at any step), the agent will terminate its execution by launching (optionally) the teardown AND failure playbooks.

## Hooks

Files located in `/etc/dci-openshift-app-agent/hooks/` need to be filled by the user.
They will NOT be replaced when the `dci-openshift-app-agent` RPM will be updated.

```
├── hooks
│   ├── install.yml
│   ├── pre-run.yml
│   ├── running.yml
│   ├── success.yml
│   ├── teardown.yml
│   └── tests.yml
```

## Samples



## Tags

To replay any steps, please use Ansible tags (--limit).

`$ cd /usr/share/dci-openshift-app-agent && source /etc/dci-openshift-app-agent/dcirc.sh && ansible-playbook -vv /usr/share/dci-openshift-app-agent/dci-openshift-app-agent.yml --tags "prepare-host,running,post-run"`

Possible tags are:

* job
* pre-run
* running
* testing
* post-run

As the `KUBECONFIG` is read from the `pre-run` tasks, this tag should always be included. 

## License

Apache License, Version 2.0 (see [LICENSE](LICENSE) file)

## Contact

Email: Distributed-CI Team <distributed-ci@redhat.com>
IRC: #distributed-ci on Freenode
