# DCI OpenShift App Agent

`dci-openshift-app-agent` enables Cloud-Native Applications and Operators in OpenShift using Red Hat Distributed CI service.
This agent is expected to be installed in a RHEL8 server (from now on referred as jumphost) with access to the API of an already deployed OCP cluster.

## Requirements

Before starting make sure the next list of items are covered in the jumphost server.

- Be running the latest stable RHEL release (**8.4 or higher**) and registered via RHSM
- Ansible 2.9 (See section [Newer Ansible Versions](#newer-ansible-versions) for newer Ansible versions)
- Access to the Internet, it could be through a proxy (See section [Proxy Considerations](#proxy-considerations))
- Access to the following repositories:
  - epel
  - dci-release
  - baseos-rpms
  - appstream-rpms
- Podman 3.0 (See section [Old Podman versions](#old-podman-versions) for older Podman versions)
- Kubernetes Python module
- An OpensShift cluster already deployed or a process to deploy it before running the `dci-openshift-app-agent`.

In an already registered server with RHEL you can fulfil the repositories and Ansible 2.9 requirements with the following commands:

```ShellSession
# subscription-manager repos --enable=rhel-8-for-x86_64-baseos-rpms
# subscription-manager repos --enable=rhel-8-for-x86_64-appstream-rpms
# subscription-manager repos --enable ansible-2.9-for-rhel-8-x86_64-rpms
# dnf -y install https://dl.fedoraproject.org/pub/epel/epel-release-latest-8.noarch.rpm
# dnf -y install https://packages.distributed-ci.io/dci-release.el8.noarch.rpm
```

## Installation

The `dci-openshift-app-agent` is packaged and available as a RPM file located in [this repository](https://packages.distributed-ci.io/dci-release.el8.noarch.rpm). It can be installed in the jumphost server with the following command:

```ShellSession
# dnf -y install dci-openshift-app-agent
```

To configure your DCI job pipelines, you need to install `dci-pipeline`. Instructions at [dci-pipeline documentation](../dci-pipeline/).

### Folders and files location

Once `dci-openshift-app-agent` package is installed, the files and resources you can find in this repository will be placed in the following locations:

- `/etc/dci-openshift-app-agent` contains these folders and files: `dcirc.sh.dist` file, `hooks` folder, `hosts.yml` file and `settings.yml` file.
- `/etc/sysconfig` folder contains the content of `sysconfig` folder, which is `dci-openshift-app-agent` file.
- `/usr/share/dci-openshift-app-agent/` gathers the following folders and files: `ansible.cfg` file, `dci-openshift-app-agent.yml` file, `group_vars` folder, `plays` folder and `utilities` folder.
- `/var/lib/dci-openshift-app-agent` folder holds the `samples` folder.
- `/usr/bin` folder holds scripts such as `dci-openshift-app-agent-ctl`.

> Note: scripts provided in this agent are deprecated. You should use `dci-pipeline` instead.

Also, have in mind that:

- `dci-openshift-app-agent` user (with sudo permissions) and group are created
- Files under `systemd` folder in this repo will be used to create the corresponding system service for `dci-openshift-app-agent`.


## Configuration

The DCI dashboard gives you a view into what jobs you have run in your distributed agent. In order to gain access to it
you have to:

1. Go to https://www.distributed-ci.io/ and click login. You will be redirected to
   sso.redhat.com so you'll use your RH account credentials.
2. If you are not part of any team you can contact an admin to get yourself
   added.
3. You will have to create a Remote CI for using it later, go on the left navigation bar on the `Remotecis` option and click.
   on "Create a new remoteci"
4. Fill out the description and which team it belongs to, then click `Create`.
5. You should see your newly created remoteci in the list, you can get
   the credentials in YAML format by click the button in the
   Authentication column. This should be saved under `~/.config/dci-pipeline/dci_credentials.yml`.

    This file allows to provide some variables to the DCI OpenShift App Agent. The table below shows the available variables and their default values.

Name                               | Default                                              | Description
---------------------------------- | ---------------------------------------------------- | -------------------------------------------------------------
dci\_config\_dir                   |                                                      | Path of the desired hooks directory
dci\_comment                       |                                                      | Comment to associate with the job
dci\_url                           |                                                      | URL to associate with the job
dci\_disconnected                  | false                                                | Set it to true if it is a disconnected environment. This variable is not defined in the default values, but all the checks that make use of this variable has a default value (i.e. false) defined.
dci\_local\_registry               | ""                                                   | Registry to fetch containers that may be used. Mandatory for disconnected environments.
provision\_cache\_store            | "/opt/cache"                                         | Directory aimed to share artifacts between dci-openshift-agent and dci-openshift-app-agent.
partner\_creds                     | ""                                                   | Authfile with registries' creds. This variable must have a value if we are on a disconnected environment. In that case, it must include the creds for the local registry used, and optionally have private registry creds for partners. If it is a connected environment, this variable is optional and, if it has a value, the file would contain just private registry creds for partners. [In this link](https://man.archlinux.org/man/community/containers-common/containers-auth.json.5.en#FORMAT), there are examples about how the files should be formatted. This variable has to be defined when running preflight on CNF Cert Suite.
dci\_workarounds                   | []                                                   | List of workarounds to be considered in the execution. Each element of the list must be a String with the following format: bz\<id> or gh-org-repo-\<id>
dci\_openshift\_app\_image         |                                                      | Image that can be to be used on the agent workloads. It needs to be defined in the partner hooks. It needs to be mirrored to a local registry in disconnected environments.
dci\_openshift\_app\_ns            | "myns"                                               | Default namespace  to deploy workloads in the running cluster.
dci\_must\_gather\_images          | ["registry.redhat.io/openshift4/ose-must-gather"]    | List of the must-gather images to use when retrieving logs.
provisioner\_name                  |                                                      | Provisioner address (name or IP) to be accessed for retrieving logs with must-gather images. If not defined, logs will not be retrieved.
provisioner\_user                  |                                                      | Provisioner username, used to access to the provisioner for retrieving logs with must-gather images. If not defined, logs will not be retrieved.
dci\_ga\_components\_for\_certification | ["ocp"]                                         | list of components that needs to be ga to submit a certification record
do\_cnf\_cert                      |false                                                 | Enable/Disable the CNF Cert Suite (<https://github.com/test-network-function/cnf-certification-test>)
do\_chart\_verifier                | false                                                | Enable/Disable the Chart Verifier
do\_must\_gather                   | true                                                 | Enable/Disable the generation of must_gather
do\_preflight\_tests               | false                                                | Trigger to activate the preflight tests
sync\_cnf\_cert\_and\_preflight    | false                                                | If true, CNF Cert Suite output (claim.json file) would be used to create the `preflight_operators_to_check` variable needed for preflight tests.
tests\_to\_verify                  | undefined                                                | List of expected test results. When defined, it triggers the validation of actual test results against the expectations. Please check [verify-tests readme](https://github.com/redhatci/ocp/tree/main/roles/verify_tests/README.md) to get more details and an example of the configuration.
|See [Operator Certification (preflight)](https://github.com/redhatci/ocp/tree/main/roles/preflight/README.md) for details to enable the Operator Certifications tests suite ||
|See [CNF-cert role](https://github.com/redhatci/ocp/tree/main/roles/cnf_cert/README.md) for details to enable the Cloud Native Functions (CNF) cert suite                   ||
|See [chart-verifier role](https://github.com/redhatci/ocp/tree/main/roles/chart_verifier/README.md) for details to enable the chart-verifier tests                          ||
|See [resources-to-components role](https://github.com/redhatci/ocp/tree/main/roles/resources_to_components/README.md) for details to enable the creation of DCI components based on Kubernetes resources deployed in the cluster, making use of `rtc_resources_to_components` variable. ||

## Pipeline job definition

Here is an example of a pipeline job definition for `dci-openshift-app-agent`:

```YAML
- name: ocp-workload
  stage: workload
  prev_stages: [ocp-upgrade, ocp]
  ansible_playbook: /usr/share/dci-openshift-app-agent/dci-openshift-app-agent.yml
  ansible_cfg: ~/my-lab-config/pipelines/ansible.cfg
  ansible_inventory: ~/my-lab-config/inventories/@QUEUE/@RESOURCE-workload.yml
  dci_credentials: ~/.config/dci-pipeline/dci_credentials.yml
  ansible_extravars:
    dci_cache_dir: ~/dci-cache-dir
    dci_config_dir: ~/my-lab-config/ocp-workload
    dci_gits_to_components:
      - ~/my-lab-config
    dci_local_log_dir: ~/upload-errors
    dci_tags: []
  use_previous_topic: true
  inputs:
    kubeconfig: kubeconfig_path
```


## Enabling the Test Suites in DCI App Agent

The DCI App Agent has support to execute multiple test suites to validate containers, virtual functions, Helm charts, and operators. The suites are in the form of Ansible roles executed during the Red Hat testing phases. The suites help the partners on getting prepared for the Red Hat Certifications or actually run the certification process on the the workloads deployed via DCI.

### Operator Certification tests

This test suite will run the command line interface for validating if OpenShift Operator Bundles and images meet minimum requirements for Red Hat [Operator Certification](https://github.com/redhat-openshift-ecosystem/openshift-preflight).

For specific details about the features and variables for this test suite see: [Preflight role](https://github.com/redhatci/ocp/tree/main/roles/preflight/README.md) documentation.

The test results for each operator can be submitted to the [Red Hat connect Site](https://connect.redhat.com/). Please see [Preflight Role](https://github.com/redhatci/ocp/tree/main/roles/preflight/README.md) documentation about how to enable this feature.

### Cloud Native Functions (CNF) Certification tests

The [CNF_cert role](https://github.com/redhatci/ocp/tree/main/roles/cnf_cert/README.md) allows the deployment of CNFs and run the defined [Tests Network Functions (TNF)](https://github.com/test-network-function/cnf-certification-test) in the order to meet minimum requirements for Red Hat OpenShift Certification.

For specific details about the features and variables for this test suite see: [CNF_cert role](https://github.com/redhatci/ocp/tree/main/roles/cnf_cert/README.md) documentation.

Also, the [tnf_test_example sample](samples/tnf_test_example/README.md) can be followed as a good example of how to deploy a workload to be tested by the CNF Cert Suite.

### Helm Chart Verifier

[Helm Chart Verifier](https://github.com/redhat-certification/chart-verifier) is a test tool that validates Helm charts based on Red Hat recommendations.

The [chart_verifier role](https://github.com/redhatci/ocp/tree/main/roles/chart_verifier/README.md) is able to deploy charts on an OCP cluster and run the helm chart verifier tests. Please see the role documentation for more details about how to run tests using via the app agent or using a pipeline.

### Test suites execution order

The test suites are executed in the following order, in the case all them are enabled.

1. Helm chart erifier
2. CNF cert
3. Preflight container only
4. Preflight operators
5. Operator SDK

Test suites may requires some delay between each execution. The following variables allow setting a pause between the execution of each test. The time must be set in minutes.
```
chart_verified_wait: 0
cnf_cert_wait: 0
```

If the execution order or pre-defined workflow does not suits the partner needs, it it recommended to use agent hooks that will allow to use the roles available for the App agent and define a custom execution workflow. See [tnf_test_example sample](samples/tnf_test_example/README.md) for a reference about the hooks structure.

## General workflow

The `dci-openshift-app-agent` is an Ansible playbook that enables Cloud-Native Applications and Operators in OpenShift using Red Hat Distributed CI service. The main entrypoint is the file `dci-openshift-app-agent.yml`. It is composed of several steps executed sequentially.

In case of an issue, the agent will terminate its execution by launching (optionally) the teardown and failure playbooks.

There are two fail statuses:

- `failure` - Whenever there's an issue with either the installation of the application or during testing.
- `error` - Whenever there's an error anywhere else during the playbook.

All the tasks prefixed with test_ will get exported in Junit using the Ansible Junit callback and submitted automatically to the DCI control server.

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

This hook is used for preparation steps required in the `jumphost` or inside the cluster. For example, it could be used to install some packages required in the `jumphost` or to prepare workload pre-requisites.

This hook is not required and can be omitted.

Tags:

- `pre-run`

### Install

This is the main hook that must take care of install and/or configure the application in the cluster.

This hook is required and will fail if not available.

Tags:

- `install`
- `running`

> There is one special stage defined between the install and tests stages, called post-install, which is defined to apply configurations that must be done between both stages. This is not an official hook that can be used by users, but it is an internal play for the agent.

### Tests

The tests hook is used to test the application in the install hook, this hook verifies and/or validates the install step in the cluster.

This hook is not required and can be omitted, but is highly recommended to define a way to validate/verify the installed application.

Tags:

- `testing`
- `running`

### Post-run

This hook is used for tasks required after the application has been installed and/or validated. For example, to upload logs to a central location, or to report the state of the application.

This hook is not required and can be omitted.

You can put your logs in `{{ job_logs.path }}` and they will be uploaded in plays/post-run.yml
 > NOTE: Test result files must follow the Junit format, must be stored within 
 the `{{ job_logs.path }}` directory and the file name must follow the pattern `*.xml`.

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
To use these samples, you need to include the variable `dci_config_dir` with the path of the sample to use in you pipeline job definition.

> NOTE: Please check the README.md for more information of how to use the examples.

1. To create a namespace and a webserver pod, to validate it is running, and to delete it, the pipeline job definition will look like this:

    workload-pipeline.yml

        ansible_extravars:
          dci_openshift_app_ns: testns
          dci_config_dir: /var/lib/dci-openshift-app-agent/samples/control_plane_example

## Storing secrets

You can store secrets in an encrypted manner in your pipeline definition files and YAML inventories by using `dci-vault` to generate your encrypted secrets. Details in the [python-dciclient documentation](../python-dciclient/).

## Job outputs

A DCI job produces a set of relevant configuration files, logs, reports, and test results that are collected during the last execution stages. The following table depicts the most relevant.

| File                                           | Section | Description                                                                               |
| ---------------------------------------------- | ------- | ----------------------------------------------------------------------------------------- |
| all-nodes.yaml                                 | Files   | The output `oc get get nodes` command                                                     |
| \<pod_name\>.log                               | Files   | The log entries for a given pod                                                           |
| \<namespace\>_events.log                       | Files   | The OCP events collected for an specific namespace                                        |
| \<namespace\>_status.log                       | Files   | The list of pods that were deployed in an specific namespace                              |
| *.log                                          | Files   | Log files generated during the job execution and stored in the `dci_log` directory        |
| *.trace                                        | Files   | Tracing files generated during the job execution and stored in the `dci_log` directory    |
| clusternetwork.yaml                            | Files   | File describing the network configuration of the cluster                                  |
| clusteroperator.txt                            | Files   | Report of the status of the cluster operators                                             |
| dci-openshift-agent-<timestamp>                | Files   | `dci-openshift-agent` tests report as JUnit format                                        |
| clusterversion.txt                             | Files   | Report of the OCP version applied to the cluster                                          |
| events.txt                                     | Files   | Output of the `oc get events -A` command                                                  |
| nodes.txt                                      | Files   | Output of the `oc get nodes -o yaml` command                                              |
| must_gather.tar.gz                             | Files   | Debugging information about your cluster, it can be used for support cases or for troubleshooting using the [O Must Gather tool](https://github.com/kxr/o-must-gather)    |
| pods.txt                                       | Files   | Output of the `oc get pods -A` command                                                    |
| tnf_config.yml                                 | Files   | The config file passed to tnf test suite (if enabled)                                     |
| dci-tnf-execution.log and cnf-certsuite.log    | Files   | The output of tnf execution, for troubleshooting purposes                                 |
| claim.json                                     | Files   | Claim file generated by the TNF test suite (if enabled)                                   |
| \<preflight_*\>                                | Files   | Multiple logs, reports, and test results generated by the execution of the preflight test suite (if enabled) |
| \<chart-name\>_*report.yaml                    | Files   | Helm chart verifier report for the chart under test                                       |
| helm-submission-report.txt                     | Files   | Report of helm charts submitted for certification (if enabled)                            |
| *junit                                         | Tests   | Processed JUnit files generated by the Job or partner tests                               |
| apirequestcounts_removed_api.csv               | Files   | This file lists the Cluster APIs used by a workload that have been marked for deprecation and removed in upcoming OCP versions |
| apirequestcounts_ocp_compatibility.xml         | Files   | The compatibility of the workload with OCP versions                                       |
| version.txt                                    | Files   | Report of the OCP client and server version using during the deployment                   |
| diff-jobs.txt                                  | Files   | A post-run stage to report that compares `the current` job versus the `previous job` of the same type regarding the components used |
| operators.json                                 | Files   | A JSON file with details about the operators installed in the cluster                     |

## Known issues

### Libvirt Considerations

If you want to test the CNF Cert Suite in a libvirt environment, remember to tag the OCP nodes to fit in the NodeSelector property defined in partner's pod (`NodeSelectors: role=partner`):

```ShellSession
for master in $(oc get node -l node-role.kubernetes.io/master -o=custom-columns=name:.metadata.name --no-headers); do \
oc label node ${master} role=partner \
done
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

#### Upgrading Ansible version

In this section from the [Ansible documentation web page](https://docs.ansible.com/ansible/latest/installation_guide/intro_installation.html#upgrading-ansible-with-pip), you can find the instructions to be followed to upgrade Ansible to a newer version.

Apart from that, it is recommended to do the following:

- Remove all Ansible packages installed via dnf
- Remove dci-* packages if already installed
- Reboot the jumphost (i.e. the server where dci-openshift-app-agent is executed)
- Reinstall Ansible from pip/pip3 as recommended in the documentation
- Reinstall dci packages

And check that everything works.

### Permissions to use Topics

You might encounter an error when running the dci-openshift-app-agent for first time with the message `Topic: XYZ Resource not found` the reasons could be the following:

- Incorrect spelling of the Topic. Login to the [DCI web dashboard](https://www.distributed-ci.io) and go to the `Topics` section in the left menu. There you could find the correct names and Topics available to use.
- If spelling is correct, then this might be a permissions issue. Ask the partner team administrator to verify the permissions on the group your account belongs.

### Problems related to UIDs while running containers with podman in localhost

Conditions in which the issue appeared:

- dci-openshift-app-agent installed.
- Execution of dci-openshift-app-agent directly using dci-openshift-app-agent-ctl, with the dci-openshift-app-agent user.
- Attempt to run a container, using podman, in localhost (e.g. tnf container for running the CNF Cert Suite).

Under these conditions, the error presented is the following (there may be other different errors, but all related to the same issue - lack of IDs available):

```Log
Error processing tar file(exit status 1): there might not be enough IDs available in the namespace (requested 0:5 for /usr/bin/write): lchown /usr/bin/write: invalid argument
 Error: unable to pull quay.io/testnetworkfunction/cnf-certification-test:unstable: unable to pull image: Error committing the finished image: error adding layer with blob "sha256:0a3cf4c29951bdca5c283957249a78290fb441c4ef2ce74f51815056e4be7e7f": Error processing tar file(exit status 1): there might not be enough IDs available in the namespace (requested 0:5 for /usr/bin/write): lchown /usr/bin/write: invalid argument
```

The problem seems to be related to the subordinate user and group mapping applied for the dci-openshift-app-agent user, a feature that is needed to run rootless containers in podman, or to isolate containers with a user namespace.

This issue has already been fixed by removing -r option when creating the dci-openshift-app-agent user in dci-openshift-app-agent.spec file. But, in case you installed dci-openshift-app-agent prior to this patch (you can check it by looking at /etc/subuid and /etc/subgid files, confirming that no entries related to dci-openshift-app-agent user are present there), you have to follow these steps:

1. Check the content of /etc/subuid and /etc/subgid files. If you have already installed dci-openshift-agent on your system, you should have an entry like this in both files:

    ```bash
    dci-openshift-agent:100000:65536
    ```

1. Copy that entry and paste it in both files, but setting the first value to dci-openshift-app-agent. If dci-openshift-agent is not installed in your server, then copy directly the line above and change the first value to dci-openshift-app-agent. Both /etc/subuid and /etc/subgid files should include a line like this now:

    ```bash
    dci-openshift-app-agent:100000:65536
    ```

1. To conclude, execute the podman system migration command, it will take care of killing the podman "pause" process and restarting the running containers with the new subuid/subgid mapping.

    ```bash
    podman system migrate
    ```

    If the containers do not restart automatically, then you can try to restart them manually.

    Make sure of changing the ownership of certain resources (e.g. the ones under /var/lib/dci-openshift-app-agent directory):

        sudo chown \
            -R \
            dci-openshift-app-agent:dci-openshift-app-agent \
            /var/lib/dci-openshift-app-agent/

    Then, you can retry to deploy the containers and it should work.

References:

- <https://access.redhat.com/solutions/4381691>
- <https://docs.docker.com/engine/security/userns-remap/>
- <https://www.redhat.com/sysadmin/debug-rootless-podman-mounted-volumes>

### Old Podman versions

It is recommended to use, at least, Podman 3.0 when running dci-openshift-app-agent, to avoid issues when pulling or building container images.

If `sudo dnf update podman` does not work, you may need to follow some of these steps:

1. Try to clean the cache just in case, and then list the available packages from the upstream repository to confirm if version 3 is listed. For example, for Podman 1.6.4, it is indeed provided by `rhel-8-for-x86_64-appstream-rpms` repo:

        $ sudo dnf clean all
        $ sudo dnf --disableexcludes all --disablerepo all --enablerepo rhel-8-for-x86_64-appstream-rpms list --available --showduplicates podman

        # If version 3 is listed, then run again:
        $ sudo dnf update podman

1. Try to find issues related to the Podman version you are using and apply the workarounds proposed. For example, for Podman 1.6.4, there was a [bug](https://github.com/containers/podman/issues/5306) related to the usage of rootless containers, in which it seems that, by removing .config and .local directories and starting from scratch, it fixed the issue.

1. Confirm that the container tools version that corresponds to Podman 3 is enabled or not, and enable it if disabled (as long as it does not impact in other workloads apart from dci-openshift-app-agent running in the server). It can be checked with the following command:

        $ sudo dnf module list container-tools

        # If container-tools rhel8 is not enabled, type the following:
        $ sudo dnf module reset container-tools
        $ sudo dnf module enable container-tools:rhel8
        # And then upgrade podman

### HMAC signature errors

When running a job, DCI app agent interacts with the API through a module called `dci-auth`, and it uses HMAC auth v4 to verify data is correct and authentic. First a signature is computed on the client side using the UTC date of the server, then another signature is computed again on DCI server. To avoid a replay attack, the signature is only valid for a few minutes. If you are running a job and see MAC errors, for example: `Hmac2Mechanism failed: signature is expired`, the server clock where the DCI agent is executed may be desynchronized.

A method to confirm this is the issue, it's to execute the command `dcictl topic-list` after sourcing the remote-ci credentials to list the topics, you might see `None` as result:

```ShellSession
$ source /etc/dci-openshift-app-agent/dcirc.sh
$ dcictl topic-list
+------+------+-------+-----------------+----------------+------------+
|  id  | name | state | component_types | export_control | product_id |
+------+------+-------+-----------------+----------------+------------+
| None | None |  None |       None      |      None      |    None    |
+------+------+-------+-----------------+----------------+------------+
```

The solution is to sync the system clock to an NTP server, the time zone is not important, use `timedatectl` command to validate if the clock is synchronized with an NTP service and enable accordingly if not.

```ShellSession
$ timedatectl
               Local time: Mon 2022-12-05 13:13:00 CST
           Universal time: Mon 2022-12-05 19:13:00 UTC
                 RTC time: Mon 2022-12-05 19:13:00
                Time zone: America/Chicago (CST, -0600)
System clock synchronized: yes
              NTP service: active
          RTC in local TZ: no
```

> NOTE: If you move the system clock around 20 minutes forward you can replicate this issue.

## Proxy Considerations

If you use a proxy to go to the Internet, export the following variables in the dci-openshift-app-agent user session where you run the agent, if you use the systemd service then it would be a good idea to store these variables in the ~/.bashrc file of the dci-openshift-app-agent user

Replace PROXY-IP:PORT with your respective settings and 10.X.Y.Z/24 with the cluster subnet of the OCP cluster, and example.com with the base domain of your cluster.

```ShellSession
export http_proxy=http://PROXY-IP:PORT
export https_proxy=http://PROXY-IP:PORT
export no_proxy=10.X.Y.Z/24,.example.com
```

> NOTE: Also consider setting the proxy settings in the /etc/rhsm/rhsm.conf file if you use the Red Hat CDN to pull packages, otherwise the agent might fail to install dependencies required during the execution of the CNF test suite.

## Testing a code change

If you want to test a code change from Gerrit, you need to have `dci-check-change` installed on your system from the `dci-openshift-agent` package.

Then for example, if you want to test the change from <https://softwarefactory-project.io/r/c/dci-openshift-app-agent/+/22647>, issue the following command:

```ShellSession
dci-check-change 22647 /var/lib/dci-openshift-agent/clusterconfigs/kubeconfig
```

You can omit the kubeconfig file as a second argument if you want `dci-check-change` to re-install OCP using `dci-openshift-agent-ctl` before testing the change.

All the other arguments will be passed to `dci-openshift-app-agent-ctl`.

## License

Apache License, Version 2.0 (see [LICENSE](LICENSE) file)

## Contact

Email: Distributed-CI Team <distributed-ci@redhat.com>
IRC: #distributed-ci on Freenode
