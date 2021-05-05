# DCI Openshift App Agent

`dci-openshift-app-agent` enables Cloud-Native Applications and Operators in OpenShift using Red Hat Distributed CI service.

## Table of Contents

- [Requirements](#requirements)
- [Workflow](#workflow)
- [Tags](#tags)
- [License](#license)
- [Contact](#contact)

## Requirements

## Worflow

The `dci-openshift-app-agent` is an Ansible playbook that enables Cloud-Native Applications and Operators in OpenShift using Red Hat Distributed CI service. The main entrypoint is the file `dci-openshift-app-agent.yml`. It is composed of several steps executed sequentially.

In case of an issue, the agent will terminate its execution by launching (optionally) the teardown and failure playbooks.

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
tnf\_operators\_regexp | "" | regexp to select operators
tnf\_cnfs\_regexp | "" |  regexp to select CNF
tnf\_exclude\_connectivity\_regexp | | regexp to exclude containers from the connectivity test
tnf\_suites | "diagnostic generic" | list of space separated [test suites](https://github.com/test-network-function/test-network-function#general)

## Launching the agent

Once the agent is configured, you can start it as a service.

Please note that the service is a systemd `Type=oneshot`. This means that if you need to run a DCI job periodically, you have to configure a `systemd timer` or a `crontab`.

```ShellSession
# systemctl start dci-openshift-app-agent
```

If you need to run the `dci-openshift-app-agent` manually in foreground,
you can use this command line:

```ShellSession
# su - dci-openshift-app-agent
$ dci-openshift-app-agent-ctl -s
```

## Tags

To replay any steps, please use Ansible tags (--tags).

```ShellSession
# su - dci-openshift-app-agent
$ dci-openshift-app-agent-ctl -s -- --tags job,pre-run,running,post-run
```

or to avoid one or multiple steps, use `--skip-tags`:

```ShellSession
# su - dci-openshift-app-agent
$ dci-openshift-app-agent-ctl -s -- --skip-tags testing
```

Possible tags are:

- `job`
- `dci`
- `kubeconfig`
- `pre-run`
- `redhat-pre-run`
- `partner-pre-run`
- `install`
- `running`
- `testing`
- `redhat-testing`
- `partner-testing`
- `post-run`

As the `KUBECONFIG` is read from the `kubeconfig` tasks, this tag should always be included.

The `dci` tag can be used to skip all DCI calls else the `job` tag is
mandatory to initialize all the DCI specifics. You will need to
provide a fake `job_info` variable in a `myvars.yml` file like this:

```YAML
job_id: fake-id
job_info:
  job:
    components:
    - name: 1.0.0
      type: my-component
```

and then call the agent like this:

```ShellSession
# su - dci-openshift-app-agent
$ dci-openshift-app-agent-ctl -s -- --skip-tags dci -e @myvars.yml
```

## License

Apache License, Version 2.0 (see [LICENSE](LICENSE) file)

## Contact

Email: Distributed-CI Team <distributed-ci@redhat.com>
IRC: #distributed-ci on Freenode
