# DCI OpenShift App Agent

`dci-openshift-app-agent` enables Cloud-Native Applications and Operators in OpenShift using Red Hat Distributed CI service.
This agent is expected to be installed in a RHEL8 server (from now on referred as jumphost) with access to the API of an already deployed OCP cluster.

## Table of Contents

- [Requirements](#requirements)
- [Installation](#installation)
- [Configuration](#configuration)
- [Launching the agent](#launching-the-agent)
  - [Running it manually](#running-it-manually)
  - [Running it as a service](#running-it-as-a-service)
  - [Using customized tags](#using-customized-tags)
- [General workflow](#general-workflow)
- [Hooks](#hooks)
  - [Pre-run](#pre-run)
  - [Install](#install)
  - [Tests](#tests)
  - [Post-run](#post-run)
  - [Teardown](#teardown)
- [Examples](#examples)
- [Development mode](#development-mode)
- [Known issues](#known-issues)
  - [Libvirt Considerations](#libvirt-considerations)
  - [Newer Ansible Versions](#newer-ansible-versions)
  - [Permissions to use Topics](#permissions-to-use-topics)
  - [Remote access to provisioner](#remote-access-to-provisioner)
  - [Problems related to UIDs while running containers with podman in localhost](#problems-related-to-uids-while-running-containers-with-podman-in-localhost)
  - [Old Podman versions](#old-podman-versions)
- [Proxy Considerations](#proxy-considerations)
- [Testing a code change](#testing-a-code-change)
- [License](#license)
- [Contact](#contact)

## Requirements

Before starting make sure the next list of items are covered in the Jumpbox server.

- Be running the latest stable RHEL release (**8.4 or higher**) and registered via RHSM
- Ansible 2.9 (See section [Newer Ansible Versions](#newer-ansible-versions) for newer Ansible versions)
- Access to the Internet, it could be through a proxy (See section [Proxy Considerations](#proxy-considerations))
- Access to the following repositories:
  - epel
  - dci-release
  - baseos-rpms
  - appstream-rpms
- Podman 3.0 (See section [Old Podman versions](#old-podman-versions) for older Podman versions)
- kubernetes python module (Optional, but most use cases will probably require it to use k8s ansible module)

In an already registered server with RHEL you can fullfil the repositories requirements with the following commands:

```ShellSession
# dnf -y install https://dl.fedoraproject.org/pub/epel/epel-release-latest-8.noarch.rpm
# dnf -y install https://packages.distributed-ci.io/dci-release.el8.noarch.rpm
# subscription-manager repos --enable=rhel-8-for-x86_64-baseos-rpms
# subscription-manager repos --enable=rhel-8-for-x86_64-appstream-rpms
```

Then install kubernetes module
```ShellSession
# dnf install python3-kubernetes
```
> NOTE: Another option is to use pip3, and you can use a more recent version of the module

## Installation

The `dci-openshift-app-agent` is packaged and available as a RPM file located in [this repository](https://packages.distributed-ci.io/dci-release.el8.noarch.rpm). It can be installed in the jumphost server with the following command:

```ShellSession
# dnf -y install dci-openshift-app-agent
```

In order to execute the `dci-openshift-app-agent`, a running OpenShift cluster, together with the credentials needed to make use of the cluster (i.e. through the `KUBECONFIG` environment variable) are needed.

The OpenShift cluster can be built beforehand by running the [DCI OpenShift Agent](https://github.com/redhat-cip/dci-openshift-agent) with the proper configuration to install the desired OCP version.

Once installed, you need to export the `kubeconfig` from the jumphost to the host in which `dci-openshift-app-agent` is executed. Then, you have set the `KUBECONFIG` environment variable to the path to the kubeconfig file in that host with `export KUBECONFIG=<path_to_kubeconfig>`

NOTE: If you followed the instructions of DCI OpenShift Agent to deploy the cluster, the `kubeconfig` file is on the provisionhost (usually located in `~/clusterconfigs/auth/kubeconfig`)

These instructions applies when using the `dci-openshift-app-agent` over both baremetal and virtual machines (libvirt) environments.

## Configuration

There are two configuration files for `dci-openshift-app-agent`:

**1. /etc/dci-openshift-app-agent/dcirc.sh**

From the [DCI web dashboard](https://www.distributed-ci.io), the partner team administrator has to create a `Remote CI` in the DCI web dashboard. Copy the relative credential and paste it locally on the Jumphost to `/etc/dci-openshift-app-agent/dcirc.sh`.

This file should be edited once:

```Shell
#!/usr/bin/env bash
DCI_CS_URL="https://api.distributed-ci.io/"
DCI_CLIENT_ID=remoteci/<remoteci_id>
DCI_API_SECRET=<remoteci_api_secret>
export DCI_CLIENT_ID
export DCI_API_SECRET
export DCI_CS_URL
```

> NOTE: The initial copy of `dcirc.sh` is shipped as `/etc/dci-openshift-app-agent/dcirc.sh.dist`. You can copy this to `/etc/dci-openshift-app-agent/dcirc.sh` to get started, then replace inline some values with your own credentials.

**2. /etc/dci-openshift-app-agent/settings.yml**

This file allows to provide some variables to the DCI OpenShift App Agent for configuration purposes. Main variables available (mainly related to the [CNF Cert Suite](https://github.com/test-network-function/test-network-function)) are the following:

Name                               | Default                                              | Description
---------------------------------- | ---------------------------------------------------- | -------------------------------------------------------------
dci\_topic                         |                                                      | Name of the topic. `OCP-4.5` and up
dci\_tags                          | ["debug"]                                            | List of tags to set on the job
dci\_name                          |                                                      | Name of the job
dci\_configuration                 |                                                      | String representing the configuration of the job
dci\_config\_dir                   |                                                      | Path of the desired hooks directory
dci\_comment                       |                                                      | Comment to associate with the job
dci\_url                           |                                                      | URL to associate with the job
dci\_components\_by\_query         | []                                                   | Component by query. ['name:4.5.9']
dci\_component                     | []                                                   | Component by UUID. ['acaf3f29-22bb-4b9f-b5ac-268958a9a67f']
dci\_previous\_job\_id             | ""                                                   | Previous job UUID
dci\_chart\_tgz\_url               | undefined                                            | The URL to an Helm chart tgz. For example: https://github.com/redhat-certification/chart-verifier/raw/main/pkg/chartverifier/checks/chart-0.1.0-v3.valid.tgz
provisionhost\_registry            | ""                                                   | registry to fetch containers that may be used. Must be set in disconnected environments.
provisionhost\_registry\_creds     | ""                                                   | path to the pull-secret.txt file to access to the registry. Must be set in disconnected environments.
dci\_openshift\_app\_image         | quay.io/testnetworkfunction/cnf-test-partner:latest  | image to be used for the workload. It can be retrieved from public repositories (i.e. Quay.io) or internal repositories (e.g. for disconnected environments)
dci\_openshift\_app\_ns            | "myns"                                               | namespace for the workload
dci\_must\_gather\_images          | ["registry.redhat.io/openshift4/ose-must-gather"]    | List of the must-gather images to use when retrieving logs.
provisioner\_name                  |                                                      | Provisioner address (name or IP) to be accessed for retrieving logs with must-gather images. If not defined, logs will not be retrieved.
provisioner\_user                  |                                                      | Provisioner username, used to access to the provisioner for retrieving logs with must-gather images. If not defined, logs will not be retrieved.
do\_cnf\_cert                      | false                                                | launch the CNF Cert Suite (https://github.com/test-network-function/test-network-function)
test\_network\_function\_version   | v3.1.0                                               | CNF Cert Suite version downloaded. The DCI OpenShift App Agent currently supports only the latest stable version, which is v3.1.0. HEAD version (in the main branch) can be also used, but it is not assured a complete compatibility with these latest unstable changes.
do\_preflight\_tests               | false                                                | Launch the [Preflight Cert Suite](https://github.com/redhat-openshift-ecosystem/openshift-preflight)
preflight\_version                 | quay.io/opdev/preflight:1.0.6                        | [Version of Preflight Cert Suite to run](https://quay.io/repository/opdev/preflight?tab=tags)
preflight\_operators\_to\_check    | undefined                                            | List of operators to be checked with Preflight Cert Suite. Please check [example_preflight_config.yaml](roles/preflight/README.md#example-of-config-file-to-define-a-list-of-operators-to-check) for the example.
operator\_sdk\_tool\_path          | undefined                                            | Path to operator-sdk binary, optional. Please check [example_preflight_config.yaml](roles/preflight/README.md#example-of-config-file-to-define-a-list-of-operators-to-check) for the example.
preflight\_namespace               | preflight-testing                                    | Namespace to use for preflight tests
submit\_preflight\_to\_pyxis       | false                                                | Should be set to true to submit Preflight results to Pyxis. Please do not forget to provide Pyxis credentials: pyxis\_apikey\_path with Pyxis token (shared for all projects within one client) and pyxis\_identifier (each operator should have its own certification project with the unique identifier).
pyxis\_apikey\_path                | undefined                                            | This is a path to file that contains partner's token. Parner should generate this token in connect.redhat.com. The token is shared for all projects within one partner.
pyxis\_identifier                  | undefined                                            | Each operator should have its own certification project with the unique identifier. If the partner has to certify two operators, he has to create two certification projects. Once a new cert project is created, the identifier could be extracted from the project url: https://connect.redhat.com/projects/pyxis_identifier/overview
tnf\_suites                        | "diagnostic access-control networking lifecycle observability platform-alteration operator"                                                                                 | list of space separated [test suites](https://github.com/test-network-function/test-network-function#general-tests).
tnf\_config                        | (see [this file](roles/cnf-cert/defaults/main.yml), as it is a complex variable)                                                                                 | Complex variable to define the configuration to be applied in CNF Cert Suite. It is composed by a list of items, each of them related to a different namespace (as CNF Cert Suite admits resources deployed in multiples namespaces). The variables that have to be defined on each item are: 1. `namespace`, which is the targeted namespace. 2. `targetpodlabels`, which is a list of autodiscovery labels to be considered by the CNF Cert Suite for pod testing. The format of each element of the list must be one of the following two: <label\_name>=<label\_value> if no prefix is provided (e.g. [environment=test]) or <label\_prefix>/<label\_name>=<label\_value> if a prefix is provided (e.g. [test-network-function.com/environment=test]). Remember to label the pods you want to test with these autodiscovery labels before executing the CNF Cert Suite. You can do it manually or programatically (an example of this can be found in [tnf_test_example](samples/tnf_test_example)). 3. (optional) `operators_regexp`, which is a regexp to select operators to be tested by the CNF Cert Suite (in case of needing it, the code to handle it must be included in the partner's hooks). And 4. (optional) `exclude_connectivity_regexp`, which is a regexp to exclude containers from the connectivity test. When deploying the pods, some code is needed to use this regex, [like in this example](https://github.com/redhat-cip/dci-openshift-app-agent/blob/master/samples/tnf_test_example/hooks/templates/test_deployment.yml.j2).
tnf\_non\_intrusive\_only          | true                                                 | set it to true if you would like to skip intrusive tests which may disrupt cluster operations. Likewise, to enable intrusive tests, set it to false
tnf\_run\_cfd\_test                | false                                                | the test suites from [openshift-kni/cnf-feature-deploy](https://github.com/openshift-kni/cnf-features-deploy) can be run prior to the actual CNF certification test execution and the results are incorporated in the same claim file if the following environment variable is set to true
tnf\_debug\_image                  | quay.io/openshift-release-dev/ocp-v4.0-art-dev@sh... | image to be used for `oc debug` command in CNF Cert Suite
tnf\_log\_level                    | "debug"                                              | log level used to run the CNF Cert Suite. Possible values can be checked [here](https://github.com/test-network-function/test-network-function#log-level)
tnf\_postrun\_delete\_resources    | true                                                 | Primarily used for debugging partner deployments when using the CNF Cert Suite. Setting to 'false' will not delete the partner deployment and the debug daemonSet during the postrun.

A minimal configuration is required for the DCI OpenShift App Agent to run, before launching the agent, make sure you have the following:

1. In /etc/dci-openshift-app-agent/settings.yml these variables are required, see their definitions in the table above. You can also define this variables in a different form, see section [Using customized tags](#using-customized-tags) below where a fake `job_info` is created.
```YAML
dci_topic:
dci_components_by_query:
dci_comment:
```
2. The DCI OpenShift App Agent by default runs a series of Ansible playbooks called hooks in phases (see section [Hooks](#hooks)). The default files only contain the string `---` and no actions are performed. The install.yml is missing on purpose, and if you run the agent at this point, you will receive an error. In that case you can choose between one of the following options to proceed:

- Create install.yml file with the string `---` and no actions will be performed at this phase.
- Create install.yml with your own tasks. (You might also consider provide tasks for all the phases: pre-run, tests, post-run, teardown)
- Include dci_config_dir variable in `settings.yml` with the path where the hooks you want to execute are located.

> See section [Examples](#examples) for basic configurations of settings.yml to start using the agent.

## Launching the agent

The agent can be executed manually or through systemd, once the agent is configured, you can start it either way.

### Running it manually
If you need to run the `dci-openshift-app-agent` manually in foreground, you can use this command line:

```ShellSession
# su - dci-openshift-app-agent
$ dci-openshift-app-agent-ctl -s
```
### Running it as a service

If you prefer to launch a job with systemd, start the dci-openshift-app-agent service

```ShellSession
# systemctl start dci-openshift-app-agent
```

> Please note that the service is a systemd `Type=oneshot`. This means that if you need to run a DCI job periodically, you have to configure a `systemd timer` or a `crontab`.

### Using customized tags

To replay any steps, the use of Ansible tags (--tags) is an option. Please refer to [Workflow](#workflow) section to understand the steps that compose the `dci-openshift-app-agent`.

```ShellSession
# su - dci-openshift-app-agent
$ dci-openshift-app-agent-ctl -s -- --tags kubeconfig,job,pre-run,running,post-run
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

```ShellSession
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

You can put your logs in {{ job\_logs.path }} and they will be uploaded in plays/post-run.yml

Tags:

- `post-run`

### Teardown

While this hook is not required it is highly recommended to be included. Its main purpose is to remove or destroy anything that was created with the install and/or the test hooks.

This hook is controlled with two variables:

- `dci_teardown_on_success` (default: true)
- `dci_teardown_on_failure` (default: false)

It's included either when there's a failure, error or at the end of all the steps.

## Examples

Some examples of hooks are provided in the $HOME directory of the `dci-openshift-app-agent` user (/var/lib/dci-openshift-app-agent/samples/). You can use those to initialize the agent tests.
To use these samples, you need to include the variable `dci_config_dir` with the path of the sample to use in the settings.yml.

> NOTE: Please check the README.md and requirements.txt files for more information of how to use the examples.

1. To create a namespace and webserver pod, validate is running, and delete it, the settings.yml file will look like this:

File: settings.yml
```YAML
dci_topic: OCP-4.8
dci_components_by_query: ['4.8.13']
dci_comment: "Test webserver"
dci_openshift_app_ns: testns
dci_config_dir: /var/lib/dci-openshift-app-agent/samples/basic_example
```

2. To validate the CNF test suite against a example workload, the settings.yml file will look like this:

File: settings.yml
```YAML
dci_topic: OCP-4.8
dci_components_by_query: ['4.8.13']
dci_comment: "Test CNF suite"
dci_openshift_app_ns: testns
dci_config_dir: /var/lib/dci-openshift-app-agent/samples/tnf_test_example
dci_openshift_app_image: quay.io/testnetworkfunction/cnf-test-partner:latest
tnf_suites: "diagnostic access-control networking lifecycle observability platform-alteration"
tnf_config: 
  - namespace: testns
    targetpodlabels: [test-network-function/environment=testing]
```

## Development mode

You can launch the agent from a local copy by passing the `-d` command line option:

```ShellSession
$ dci-openshift-app-agent-ctl -s -d
```

`dcirc.sh` is read from the current directory instead of `/etc/dci-openshift-app-agent/dcirc.sh`.

You can override the location of `dci-ansible` using the `DCI_ANSIBLE_DIR` environment variable.

You can add extra paths for Ansible roles using the
`DCI_ANSIBLE_ROLES` environment variable separating paths by `:`.

## Known issues

### Libvirt Considerations

If you want to test the CNF Cert Suite in a libvirt environment, remember to tag the OCP nodes to fit in the NodeSelector property defined in partner's pod (`NodeSelectors: role=partner`):

```ShellSession
# for X in 0:n, with n = { number of master nodes - 1 }
oc label node master-X role=partner
```

### Newer Ansible Versions

Red Hat Enterprise Linux 8 defaults to Ansible 2.9 installed from Ansible or base repositories, it is highly recommended to use this version because using Ansible >= 2.10 requires newer versions of other python modules that can affect your entire server. You can install Ansible 2.10 or Ansible core (2.11) via other methods, but because starting at 2.10 the use of collections has introduced some changes, you need to install a few collections to make it work

After installing the agent, login as dci-openshift-app-agent user and install the following collections

```ShellSession
# su - dci-openshift-app-agent
$ ansible-galaxy collection install community.kubernetes
$ ansible-galaxy collection install community.general
```
Also the use of newer Ansible versions requires a recent version of the kubernetes python module ( >= 12.0.0), as today only available through pip3

You can upgrade the current version for the dci-openshift-app-agent user only or install a specific version like this:
```ShellSession
$ python3 -m pip install -U kubernetes --user
# or
$ python3 -m pip install kubernetes==12.0.1 --user
```

### Permissions to use Topics

You might encounter an error when running the dci-openshift-app-agent for first time with the message `Topic: XYZ Resource not found` the reasons could be the following:

- Incorrect spelling of the Topic. Login to the [DCI web dashboard](https://www.distributed-ci.io) and go to the `Topics` section in the left menu. There you could find the correct names and Topics available to use.
- If spelling is correct, then this might be a permissions issue. Ask the partner team administrator to verify the permissions on the group your account belongs.

### Remote access to provisioner

Note that have to add the SSH public key of the user that runs the "dci-openshift-app-agent-ctl" command to SSH "provisioner_name" with "provisioner_user", in case you want to retrieve logs from the OCP deployment.

### Problems related to UIDs while running containers with podman in localhost

Conditions in which the issue appeared:

- dci-openshift-app-agent installed.
- Execution of dci-openshift-app-agent directly using dci-openshift-app-agent-ctl, with the dci-openshift-app-agent user.
- Attempt to run a container, using podman, in localhost (e.g. tnf container for running the CNF Cert Suite).

Under these conditions, the error presented is the following (there may be other different errors, but all related to the same issue - lack of IDs available):

```
Error processing tar file(exit status 1): there might not be enough IDs available in the namespace (requested 0:5 for /usr/bin/write): lchown /usr/bin/write: invalid argument
 Error: unable to pull quay.io/testnetworkfunction/test-network-function:unstable: unable to pull image: Error committing the finished image: error adding layer with blob "sha256:0a3cf4c29951bdca5c283957249a78290fb441c4ef2ce74f51815056e4be7e7f": Error processing tar file(exit status 1): there might not be enough IDs available in the namespace (requested 0:5 for /usr/bin/write): lchown /usr/bin/write: invalid argument
```

The problem seems to be related to the subordinate user and group mapping applied for the dci-openshift-app-agent user, a feature that is needed to run rootless containers in podman, or to isolate containers with a user namespace.

This issue has already been fixed by removing -r option when creating the dci-openshift-app-agent user in dci-openshift-app-agent.spec file. But, in case you installed dci-openshift-app-agent prior to this patch (you can check it by looking at /etc/subuid and /etc/subgid files, confirming that no entries related to dci-openshift-app-agent user are present there), you have to follow these steps:

1. Check the content of /etc/subuid and /etc/subgid files. If you have already installed dci-openshift-agent on your system, you should have an entry like this in both files:

```bash
$ dci-openshift-agent:100000:65536
```

2. Copy that entry and paste it in both files, but setting the first value to dci-openshift-app-agent. If dci-openshift-agent is not installed in your server, then copy directly the line above and change the first value to dci-openshift-app-agent. Both /etc/subuid and /etc/subgid files should include a line like this now:

```bash
$ dci-openshift-app-agent:100000:65536
```

3. Stop and delete all containers that may be running on podman.

```bash
podman stop $(podman ps -a -q)
podman rm $(podman ps -a -q)
```

4. Kill processes related to podman:

```bash
ps -fe | grep podman | grep -v grep
# kill the processes obtained with kill -9 <pid>
```

5. To conclude, execute the following (it should not be necessary but just in case there are some containers running):

```bash
podman system migrate
```

Make sure of changing the ownership of certain resources (e.g. the ones under /var/lib/dci-openshift-app-agent directory):

```bash
sudo chown dci-openshift-app-agent:dci-openshift-app-agent -R /var/lib/dci-openshift-app-agent/
```

Then, you can retry to deploy the containers and it should work.

References:

- https://access.redhat.com/solutions/4381691
- https://docs.docker.com/engine/security/userns-remap/

### Old Podman versions

It is recommended to use, at least, Podman 3.0 when running dci-openshift-app-agent, to avoid issues when pulling or building container images.

If `sudo dnf update podman` does not work, you may need to follow some of these steps:

1. Try to clean the cache just in case, and then list the available packages from the upstream repository to confirm if version 3 is listed. For example, for Podman 1.6.4, it is indeed provided by `rhel-8-for-x86_64-appstream-rpms` repo:

```ShellSession
$ sudo dnf clean all
$ sudo dnf --disableexcludes all --disablerepo all --enablerepo rhel-8-for-x86_64-appstream-rpms list --available --showduplicates podman

# If version 3 is listed, then run again:
$ sudo dnf update podman
```

2. Try to find issues related to the Podman version you are using and apply the workarounds proposed. For example, for Podman 1.6.4, there was a [bug](https://github.com/containers/podman/issues/5306) related to the usage of rootless containers, in which it seems that, by removing .config and .local directories and starting from scratch, it fixed the issue.

3. Confirm that the container tools version that corresponds to Podman 3 is enabled or not, and enable it if disabled (as long as it does not impact in other workloads apart from dci-openshift-app-agent running in the server). It can be checked with the following command:

```ShellSession
$ sudo dnf module list container-tools

# If container-tools rhel8 is not enabled, type the following:
$ sudo dnf module reset container-tools
$ sudo dnf module enable container-tools:rhel8
# And then upgrade podman
```

## Proxy Considerations

If you use a proxy to go to the Internet, export the following variables in the dci-openshift-app-agent user session where you run the agent, if you use the systemd service then it would be a good idea to store these variables in the ~/.bashrc file of the dci-openshift-app-agent user

Replace PROXY-IP:PORT with your respective settings and 10.X.Y.Z/24 with the cluster subnet of the OCP cluster, and example.com with the base domain of your cluster.

```ShellSession
$ export http_proxy=http://PROXY-IP:PORT
$ export https_proxy=http://PROXY-IP:PORT
$ export no_proxy=10.X.Y.Z/24,.example.com
```

> NOTE: Also consider setting the proxy settings in the /etc/rhsm/rhsm.conf file if you use the Red Hat CDN to pull packages, otherwise the agent might fail to install dependencies required during the execution of the CNF test suite.

## Testing a code change

If you want to test a code change from Gerrit, you need to have `dci-check-change` installed on your system from the `dci-openshift-agent` package.

Then for example, if you want to test the change from https://softwarefactory-project.io/r/c/dci-openshift-app-agent/+/22647, issue the following command:

```ShellSession
$ dci-check-change 22647 /var/lib/dci-openshift-agent/clusterconfigs/kubeconfig -e do_preflight_tests=true
```

You can omit the kubeconfig file as a second argument if you want `dci-check-change` to re-install OCP using `dci-openshift-agent-ctl` before testing the change.

All the other arguments will be passed to `dci-openshift-app-agent-ctl`.

## License

Apache License, Version 2.0 (see [LICENSE](LICENSE) file)

## Contact

Email: Distributed-CI Team <distributed-ci@redhat.com>
IRC: #distributed-ci on Freenode
