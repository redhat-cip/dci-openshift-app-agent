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

In case of an issue, the agent will terminate its execution by launching (optionally) the teardown AND failure playbooks.

There are two fail statuses:

- `failure` - Whenever there's an issue with either the installation of the application or during testing.
- `error` - Whenever there's an error anywhere else during the playbook.

## Hooks

Files located in `/etc/dci-openshift-app-agent/hooks/` need to be filled by the user.
They will NOT be replaced when the `dci-openshift-app-agent` RPM will be updated.

```bash
├── hooks
│   ├── pre-run.yml
│   ├── install.yml
│   ├── tests.yml
│   ├── post-run.yml
│   └── teardown.yml
```

### Pre-run

This hook is used for preparation steps required in the `jumphost` or anywhere else _outside the cluster_. For example, it could be used to install some packages required in the `jumphost` or to report the state of the cluster before starting.

This hook is not required and can be omitted.

Tags:

- `pre-run`

### Install

This is the main hook that must take care of install and/or configure the application in the cluster.

This hook is required and will fail if not available.

Tags:

- `install`
- `running`

### Tests

The tests hook is used to test the application in the install hook, this hook verifies and/or validates the install step in the cluster.

This hook is not required and can be omitted, but is highly recommended to define a way to validate/verify the installed application.

Tags:

- `testing`
- `running`

### Post-run

This hook is used for tasks required after the application has been installed and/or validated. For example, to upload logs to a central location, or to report the state of the application.

This hook is not required and can be omitted.

Tags:

- `post-run`

### Teardown

While this hook is not required it is highly recommended to be included. Its main purpose is to remove or destroy anything that was created with the install and/or the test hooks.

This hook is controlled with two variables:

- `dci_teardown_on_success`
- `dci_teardown_on_failure`

It's included either when there's a failure or at the end of all the steps.

## Variables

Name | Default | Description
------------ | ------------- | -------------
dci\_openshift\_app\_ns | | namespace for the workload
 do\_cnf\_cert | false | launch the CNF Cert Suite (https://github.com/test-network-function/test-network-function)

## Tags

To replay any steps, please use Ansible tags (--limit).

```bash
$ cd /usr/share/dci-openshift-app-agent &&
  source /etc/dci-openshift-app-agent/dcirc.sh &&
  ansible-playbook -vv /usr/share/dci-openshift-app-agent/dci-openshift-app-agent.yml \
  --tags "pre-run,running,post-run"
```

Possible tags are:

- `job`
- `pre-run`
- `install`
- `running`
- `testing`
- `post-run`

As the `KUBECONFIG` is read from the `pre-run` tasks, this tag should always be included.

## License

Apache License, Version 2.0 (see [LICENSE](LICENSE) file)

## Contact

Email: Distributed-CI Team <distributed-ci@redhat.com>
IRC: #distributed-ci on Freenode
