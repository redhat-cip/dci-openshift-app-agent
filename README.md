# DCI Openshift App Agent

`dci-openshift-app-agent` enables Cloud-Native Applications and Operators in OpenShift using Red Hat Distributed CI service.

## Table of Contents

- [Requirements](#requirements)
- [Configuration](#configuration)
- [Launching the agent](#launching-the-agent)
  - [Using customized tags](#using-customized-tags)
- [General workflow](#general-workflow)
- [Hooks](#hooks)
  - [Pre-run](#pre-run)
  - [Install](#install)
  - [Tests](#tests)
  - [Post-run](#post-run)
  - [Teardown](#teardown)
- [Known issues](#known-issues)
- [License](#license)
- [Contact](#contact)

## Requirements

The `dci-openshift-app-agent` is packaged and available as a RPM file located in [this repository](https://packages.distributed-ci.io/dci-release.el8.noarch.rpm). It can be installed with the following command:

```bash
dnf -y install dci-openshift-app-agent
```

Once installed, to execute the `dci-openshift-app-agent`, a running OpenShift cluster, together with the credentials needed to make use of the cluster (i.e. through the `KUBECONFIG` environment variable) are needed.

The OpenShift cluster can be built beforehand by running the [DCI OpenShift Agent](https://github.com/redhat-cip/dci-openshift-agent) with the proper configuration to install the desired OCP version. 

Once installed, you need to export the `kubeconfig` file from the provisionhost (usually located in `~/clusterconfigs/auth/kubeconfig`) to the host in which `dci-openshift-app-agent` is executed. Then, you have set the `KUBECONFIG` environment variable to the path to the kubeconfig file in that host with `export KUBECONFIG=<path_to_kubeconfig>` 

These instructions applies when using the `dci-openshift-app-agent` over both baremetal and virtual machines (libvirt) environments.

## Configuration

There are two configuration files for `dci-openshift-app-agent`: `/etc/dci-openshift-app-agent/dcirc.sh` and `/etc/dci-openshift-app-agent/settings.yml`.

- `/etc/dci-openshift-app-agent/dcirc.sh`

Note: The initial copy of `dcirc.sh` is shipped as `/etc/dci-openshift-app-agent/dcirc.sh.dist`.

Copy this to `/etc/dci-openshift-app-agent/dcirc.sh` to get started, then replace inline some values with your own credentials.

From the web the [DCI web dashboard](https://www.distributed-ci.io), the partner team administrator has to create a `Remote CI` in the DCI web dashboard.

Copy the relative credential and paste it locally on the Jumpbox to `/etc/dci-openshift-app-agent/dcirc.sh`.

This file should be edited once:

```bash
#!/usr/bin/env bash
DCI_CS_URL="https://api.distributed-ci.io/"
DCI_CLIENT_ID=remoteci/<remoteci_id>
DCI_API_SECRET=<remoteci_api_secret>
export DCI_CLIENT_ID
export DCI_API_SECRET
export DCI_CS_URL
```

- `/etc/dci-openshift-app-agent/settings.yml`

This file allows to provide some variables to the DCI OpenShift App Agent for configuration purposes. Main variables available (mainly related to the [CNF Cert Suite](https://github.com/test-network-function/test-network-function)) are the following:

Name                               | Default                                              | Description
---------------------------------- | ---------------------------------------------------- | -------------------------------------------------------------
dci\_topic                         |                                                      | Name of the topic. `OCP-4.5` and up
dci\_tags                          | ["debug"]                                            | List of tags to set on the job
dci\_name                          |                                                      | Name of the job
dci\_configuration                 |                                                      | String representing the configuration of the job
dci\_comment                       |                                                      | Comment to associate with the job
dci\_url                           |                                                      | URL to associate with the job
dci\_components\_by\_query         | []                                                   | Component by query. ['name:4.5.9']
dci\_component                     | []                                                   | Component by UUID. ['acaf3f29-22bb-4b9f-b5ac-268958a9a67f']
provisionhost\_registry            | ""                                                   | registry to fetch containers that may be used. Must be set in disconnected environments.
provisionhost\_registry\_creds     | ""                                                   | path to the pull-secret.txt file to access to the registry. Must be set in disconnected environments.
dci\_openshift\_app\_image         | quay.io/testnetworkfunction/cnf-test-partner:latest  | image to be used for the workload. It can be retrieved from public repositories (i.e. Quay.io) or internal repositories (e.g. for disconnected environments)
dci\_openshift\_app\_ns            |                                                      | namespace for the workload
do\_cnf\_cert                      | false                                                | launch the CNF Cert Suite (https://github.com/test-network-function/test-network-function)
test\_network\_function\_version   | v3.0.0                                               | CNF Cert Suite version downloaded. The DCI OpenShift App Agent currently supports v1.0.8, v2.0.0 and v3.0.0
tnf\_operators\_regexp             | ""                                                   | regexp to select operators. Only for versions equal or lower to v2.0.0
tnf\_cnfs\_regexp                  | ""                                                   | regexp to select CNF. Only for versions equal or lower to v2.0.0
tnf\_exclude\_connectivity\_regexp | ""                                                   | regexp to exclude containers from the connectivity test
tnf\_suites                        | "diagnostic"                                         | list of space separated [test suites](https://github.com/test-network-function/test-network-function#general-tests). Note that, for versions until v2.0.0, you can execute the following test suites: diagnostic, generic, container, operator, multus. For versions from v3.0.0, you can execute the following tests: diagnostic, access-control, networking, lifecycle, observability, platform-alteration, operator, affiliated-certification
tnf\_targetpodlabels\_name         | ""                                                   | for CNF Cert Suite v3.0.0, name of the label to be attached to the workload created, then using it in the CNF Cert Suite configuration file for retrieving automatically the workload. Not to be used for versions equal or lower to v2.0.0
tnf\_targetpodlabels\_value        | ""                                                   | for CNF Cert Suite v3.0.0, value of the label to be attached to the workload created, then using it in the CNF Cert Suite configuration file for retrieving automatically the workload. Not to be used for versions equal or lower to v2.0.0
tnf\_non\_intrusive\_only          | true                                                 | for CNF Cert Suite v3.0.0, set it to true if you would like to skip intrusive tests which may disrupt cluster operations. Likewise, to enable intrusive tests, set it to false. Not to be used for versions equal or lower to v2.0.0
verify\_cnf\_features              | false                                                | for CNF Cert Suite v3.0.0, the test suites from [openshift-kni/cnf-feature-deploy](https://github.com/openshift-kni/cnf-features-deploy) can be run prior to the actual CNF certification test execution and the results are incorporated in the same claim file if the following environment variable is set to true. Not to be used for versions equal or lower to v2.0.0

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

### Using customized tags

To replay any steps, please use Ansible tags (--tags). Please refer to [Workflow](#workflow) section to understand the steps that compose the `dci-openshift-app-agent`.

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
- `success`

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

## General workflow

The `dci-openshift-app-agent` is an Ansible playbook that enables Cloud-Native Applications and Operators in OpenShift using Red Hat Distributed CI service. The main entrypoint is the file `dci-openshift-app-agent.yml`. It is composed of several steps executed sequentially.

In case of an issue, the agent will terminate its execution by launching (optionally) the teardown and failure playbooks.

There are two fail statuses:

- `failure` - Whenever there's an issue with either the installation of the application or during testing.
- `error` - Whenever there's an error anywhere else during the playbook.

## Hooks

Files located in `/etc/dci-openshift-app-agent/hooks/` need to be filled by the user.

They will NOT be replaced when the `dci-openshift-app-agent` RPM is updated.

The hooks that can be defined are the following:

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

- `dci_teardown_on_success` (default: true)
- `dci_teardown_on_failure` (default: false)

It's included either when there's a failure or at the end of all the steps.

## Known issues

- If you want to test the CNF Cert Suite in a libvirt environment, remember to tag the OCP nodes to fit in the NodeSelector property defined in partner's pod (`NodeSelectors: role=partner`):

```bash
# for X in 0:n, with n = { number of master nodes - 1 }
oc label node master-X role=partner
```

## License

Apache License, Version 2.0 (see [LICENSE](LICENSE) file)

## Contact

Email: Distributed-CI Team <distributed-ci@redhat.com>
IRC: #distributed-ci on Freenode
