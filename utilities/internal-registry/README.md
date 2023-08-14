# Enabling the local OCP images registry

Some test suites may require a local registry to load/pull container images, in cases where a registry is not available the internal registry can be useful.

This playbook helps enabling the OCP integrated registry on an already created cluster, configuring it with ephemeral storage. Please note that all the images are lost if you restart the registry.

Also it is important to notice that enabling the internal registry will configure the cluster nodes to be able to pull from the internal registry endpoint, this requires changes applied via Machine Configs that will execute a cluster nodes rolling restart causing some delays or pods distruption depending on the cluster size.

**The usage of this configuration is not recommended for production environments.**

The following is a list of actions performed by this playbook:
1. The internal registry is enabled on the cluster.
1. The internal registry is configured with ephemeral storage.
1. The internal registry is exposed via a the cluster's default route.
1. A new identity provider based in httpd backed is created.
1. A new user called `ocp_registry_user` is created and granted with read/write access to the registry.
1. The cluster's global pull secrets is updated withm the `ocp_registry_user` credentials.
1. Access to the internal registry is allowed on the cluster's nodes by adding it as insecure registry (this will perform a rolling restart on the cluster nodes).

The above actions are reverted by the `disable_ocp_registry` flag, except for the restoration of the original pull secret. Please see the [Recommendations](#recommendations) section for more information.

## Requirements

In order to execute the playbook the following requirements must be available:

1. A running OpenShift cluster with the proper credentials is required, credentials can be passed as the KUBECONFIG environment variable or using the kubeconfig extra-var.

1. The `oc` command must be available in the PATH.

1. The community.kubernetes ansible collections must be installed.

## Recommendations

It is recommended to backup the global cluster pull secrets before enabling the internal registry and restore them once it is decided to disable the internal registry.

Backing up the global cluster pull secrets is done by the following command:

```ShellSession
oc get secret/pull-secret -n openshift-config --template='{{index .data ".dockerconfigjson" | base64decode}}' > global_pull_secret
```

Restoring the global cluster pull secrets is done by the following command:
```ShellSession
oc set data secret/pull-secret -n openshift-config --from-file=.dockerconfigjson=global_pull_secret
```

Please take backup on any other important data before enabling the internal registry.

## Variables
Name                               | Default                        | Required                          | Description
---------------------------------- | -------------------------------|---------------------------------- | -------------------------------------------------------------
kubeconfig                         | undefined                      | true                              | The path to the kubeconfig file.
enable_ocp_registry                | false                          | false                             | Enables and exposes the internal OCP images registry.
disable_ocp_registry               | false                          | false                             | Disables the internal OCP images registry.

If `enable_ocp_registry` is set to true, the registry endpoint will be exposed via the default cluster route, something like: default-route-openshift-image-registry.apps.<cluster_name>.<domain> and the service endpoint image-registry.openshift-image-registry.svc:5000. The registry is configured using self signed certificates.

Running the following command will enable the registry:
```ShellSession
ansible-playbook -e enable_ocp_registry=true internal-registry.yml -v
```

Running the following command will disable the registry:
```ShellSession
ansible-playbook -e disable_ocp_registry=true internal-registry.yml
```

## Working with the registry

After running the installation, the following variables related to the registry will be available. Other registry details will be shown as the play outputs.

`ocp_registry_user`: The user to be used to access the registry.

`ocp_registry_user_token`: The token used to authenticate to the registry.

`ocp_registry_endpoint`: The endpoint of the registry.

A directory with registry access credentials and some backups of the cluster configs will be created in the current play directory.

- Login to the registry:
```ShellSession
$ podman login -u ocp_registry_user -p <ocp_registry_user_token> --tls-verify=false $HOST
```

- How to pull/tag/push images to the registry that can be used later by the test suites:
```ShellSession
$ podman pull name.io/image
$ podman tag name.io/image default-route-openshift-image-registry.apps.<cluster_name>.<domain>/<project>/image:latest
$ podman push --tls-verify=false default-route-openshift-image-registry.apps.<cluster_name>.<domain>/<project>/image:latest
```

The proper DNS resolution and network configuration should be in place in order to allow the registry to be reached from outside the cluster.

## License

Apache License, Version 2.0 (see [LICENSE](../../LICENSE) file)

## Contact

Email: Telco CI <telcoci@redhat.com>
IRC: #distributed-ci on Freenode
