# Detach ZTP spoke cluster

This sample performs the spoke cluster detachment from a given hub cluster, with the particularity that the spoke cluster was created based on ZTP-GitOps approach.

The following roles from redhatci.ocp collection are called:

- [redhatci.ocp.remove_ztp_gitops_resources](https://github.com/redhatci/ansible-collection-redhatci-ocp/blob/main/roles/remove_ztp_gitops_resources/README.md): Remove all GitOps related resources for a given spoke cluster, excepting the cluster namespace, which is not deleted because this will imply the spoke cluster is detached from the hub cluster.
- [redhatci.ocp.acm_spoke_mgmt](https://github.com/redhatci/ansible-collection-redhatci-ocp/blob/main/roles/acm_spoke_mgmt/README.md): This role allows to perform multiple management operations related to a spoke cluster,e.g. attach a spoke cluster to a given hub cluster, or detach a spoke cluster from a given hub cluster.

# Inventory example

```
---

all:
  hosts:
    jumphost:
      ansible_connection: local
  vars:
    spoke_cluster_name: bevo2

...
```

# Pipeline example

Note this example takes the following input variables from previous pipelines: `hub_kubeconfig` and `spoke_kubeconfig`, which are forwarded to outputs.

```
---

- name: ztp-detach-spoke
  stage: ztp-detach-spoke
  prev_stages: [acm-hub, ztp-spoke]
  ansible_playbook: /usr/share/dci-openshift-app-agent/dci-openshift-app-agent.yml
  ansible_cfg: /path/to/ansible.cfg
  ansible_inventory: /path/to/inventory
  configuration: "@QUEUE"
  dci_credentials: ~/.config/dci-pipeline/credentials.yml
  ansible_extravars:
    dci_config_dir: /var/lib/dci-openshift-app-agent/samples/day_2_cluster_operations/detach_ztp_spoke_cluster
    dci_workarounds: []
  use_previous_topic: true
  # - retrieve `hub_kubeconfig` input file and save the content in `kubeconfig_path` variable
  # (`kubeconfig_path` can be extracted also from dci-pipeline call if launching a CNF pipeline on
  # top of a running cluster)
  # - retrieve `spoke_kubeconfig` input file and save the content in `spoke_cluster_kubeconfig_path` variable
  # (`spoke_cluster_kubeconfig_path` can be extracted also from the proposed inventory file)
  inputs:
    hub_kubeconfig: kubeconfig_path
    spoke_kubeconfig: spoke_cluster_kubeconfig_path
  # - save the content of `hub_kubeconfig` variable in `hub_kubeconfig` output file
  # - save the content of `spoke_kubeconfig` variable in `spoke_kubeconfig` output file
  # These variables are created in the post-run hook
  outputs:
    hub_kubeconfig: hub_kubeconfig
    spoke_kubeconfig: spoke_kubeconfig

...
```
