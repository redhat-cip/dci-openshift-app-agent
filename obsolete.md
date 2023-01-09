# Old way to use the dci-openshift-app-agent

In order to execute the `dci-openshift-app-agent`, a running OpenShift cluster, together with the credentials needed to make use of the cluster (i.e. through the `KUBECONFIG` environment variable) are needed.

## Installation

The OpenShift cluster can be built beforehand by running the [DCI OpenShift Agent](../dci-openshift-agent) with the proper configuration to install the desired OCP version.

Once installed, you need to export the `kubeconfig` from the jumphost to the host in which `dci-openshift-app-agent` is executed. Then, you have set the `KUBECONFIG` environment variable to the path to the kubeconfig file in that host with `export KUBECONFIG=<path_to_kubeconfig>`

> NOTE: If you followed the instructions of DCI OpenShift Agent to deploy the cluster, the `kubeconfig` file is on the provisionhost (usually located in `~/clusterconfigs/auth/kubeconfig`)

These instructions applies when using the `dci-openshift-app-agent` over both baremetal and virtual machines (libvirt) environments.

## Configuration

A minimal configuration is required for the DCI OpenShift App Agent to run, before launching the agent, make sure you have the following:

1. In /etc/dci-openshift-app-agent/settings.yml these variables are required, see their definitions in the table above. You can also define this variables in a different form, see section [Using customized tags](#using-customized-tags) below where a fake `job_info` is created.

        dci_topic:
        dci_components_by_query:
        dci_comment:

1. The DCI OpenShift App Agent by default runs a series of Ansible playbooks called hooks in phases (see section [Hooks](#hooks)). The default files only contain the string `---` and no actions are performed. The install.yml is missing on purpose, and if you run the agent at this point, you will receive an error. In that case you can choose between one of the following options to proceed:

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

> NOTE: The service is a systemd `Type=oneshot`. This means that if you need to run a DCI job periodically, you have to configure a `systemd timer` or a `crontab`.

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

The `dci` tag can be used to skip all DCI calls else the `job` tag is mandatory to initialize
all the DCI specifics. If you cannot do the DCI calls, you just need to call the agent like this:

```ShellSession
# su - dci-openshift-app-agent
$ dci-openshift-app-agent-ctl -s -- --skip-tags dci
```

## Overloading settings and hooks directories

To allow storing the settings and the hooks in a different directory,
you can set `/etc/dci-openshift-agent/config` like this:

```console
CONFIG_DIR=/var/lib/dci-openshift-app-agent/config
```

This will allow you to use a version control system for all your settings.

If you want to also store the hooks in the same directory, you have to specify `dci_config_dir` in your `settings.yml`. Example:

```YAML
---
dci_config_dir: [/var/lib/dci-openshift-app-agent/config]
```

## Development mode

You can launch the agent from a local copy by passing the `-d` command line option:

```ShellSession
dci-openshift-app-agent-ctl -s -d
```

`dcirc.sh` is read from the current directory instead of `/etc/dci-openshift-app-agent/dcirc.sh`.

You can override the location of `dci-ansible` using the `DCI_ANSIBLE_DIR` environment variable.

You can add extra paths for Ansible roles using the
`DCI_ANSIBLE_ROLES` environment variable separating paths by `:`.

## Override the default settings file

You can use `-c` command line option to override the default settings file used by the agent.

```ShellSession
$ dci-openshift-app-agent-ctl -s -c <path/to/settings.yml>
```

Another way of overriding the settings used by the agent is the prefix mechanism, which can
be activated with `-p` command line option. In this way, both settings and hosts files will
be taken from the configuration directory you have configured (if using `CONFIG_DIR` variable,
both exporting it or including it in `/etc/dci-openshift-app-agent/config` file; else the
configuration directory will be `/etc/dci-openshift-app-agent` by default). Also, another
requirement is that settings and hosts file have to be prefixed with `<prefix>-`.

```ShellSession
$ dci-openshift-app-agent-ctl -s -p <prefix>
```

In case of using `-c` and `-p` together, `-p` takes precedence (in case the requirements
commented above are met, else the settings file provided with `-c` would be used).
