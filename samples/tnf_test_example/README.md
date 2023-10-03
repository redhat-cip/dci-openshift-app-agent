# TNF Test example

This example deploys a couple of pods in different namespaces, to be used with the CNF Test Suite provided by [test-network-function](https://github.com/test-network-function/cnf-certification-test) in a multi-namespace scenario.

Note that this example works in OCP versions equal or higher than 4.8.x.

A possible configuration to deploy this sample is the following (note that variables that are not defined, such as the ones related to `cnf_cert` role, would use default values):

```yaml
---
dci_tags: ["debug"]
dci_config_dir: "/var/lib/dci-openshift-app-agent/samples/tnf_test_example"
dci_components_by_query: ["type:tnf_test_example"]
do_cnf_cert: true
tnf_config:
  - namespace: "test-cnf"
    targetpodlabels: [environment=test]
    targetoperatorlabels: [operators.coreos.com/mongodb-enterprise.test-cnf=]
    target_crds:
      - nameSuffix: "crdexamples.test-network-function.com"
        scalable: false
    exclude_connectivity_regexp: ""
  - namespace: "production-cnf"
    targetpodlabels: [environment=production]
    targetoperatorlabels: []
    target_crds:
      - nameSuffix: "crdexamples.test-network-function.com"
        scalable: false
    exclude_connectivity_regexp: ""
...
```

In particular, two namespaces are created, called `test-cnf` and `production-cnf`, mimic-ing the two typical environments we can find to deploy application workloads. In the first case, a Deployment is used to create the pods, and in the second case, it is used a StatefulSet.

Other resources related to the pods under test are also deployed:

- Configuration for istio injection, in order to install istio-proxy container on each pod, if istio/Aspenmesh is installed in the cluster. This is only done if `tnf_enable_service_mesh` control flag is set to `true` (`false` by default).
- (If no default StorageClass is present in the cluster) Local StorageClass and PersistentVolumes, attached to the pods under test in `production-cnf` namespace.
- A custom SCC applied to all the pods. This SCC follows the Verizon recommendations to use best practices for deploying pods securely.
- Resource quotas, extracted from [this repository](https://github.com/test-network-function/cnf-certification-test-partner/blob/main/test-target/resource-quota.yaml).
- Network policies, extracted from these sources: [(1)](https://github.com/test-network-function/cnf-certification-test-partner/blob/main/test-target/ingress-deny-all-np.yaml), [(2)](https://github.com/test-network-function/cnf-certification-test-partner/blob/main/test-target/egress-deny-all-np.yaml) and [(3)](https://github.com/test-network-function/cnf-certification-test-partner/blob/main/test-target/pod-to-pod-np.yaml).
- CRD under test, extracted from [this repository](https://github.com/test-network-function/cnf-certification-test-partner/blob/main/test-target/local-crd-under-test.yaml).
- Pod disruption budget, extracted from [this repository](https://github.com/test-network-function/cnf-certification-test-partner/blob/main/test-target/pod-disruption-budget.yaml).
- Hugepages configuration in the pods under test, extracted from [this repository](https://github.com/test-network-function/cnf-certification-test-partner/tree/main/examples/platform).
  - Note that, to use this feature, you need to activate `tnf_enable_hugepages: true` in your code (default to `false`).
- Affinity rules applied to the pods under test. In the case of `test-cnf` namespace, pods are deployed using `podAntiAffinity` rule to keep the pods in different worker nodes, and in `production-cnf` namespace, a `podAffinity` rule is used to keep the pods in the same worker node, also using `AffinityRequired: 'true'` label.
- Pods in `test-cnf` namespace are deployed with non-guaranteed QoS, whereas pods in `production-cnf` are deployed with guaranteed QoS, together with certain CPU allocation constraints and runtime class definition.

Finally, apart from the pods under test, it also deploys, in one of the namespaces:

- An operator, which can be based on [mongodb-enterprise](https://catalog.redhat.com/software/operators/detail/5e9872923f398525a0ceafba) or in [simple-demo-operator](https://github.com/redhat-openshift-ecosystem/certified-operators/tree/main/operators/simple-demo-operator), in order to execute CNF Cert Suite and Preflight tests over this operator.
- A Helm chart, based on [fredco samplechart](https://github.com/openshift-helm-charts/charts/tree/main/charts/partners/fredco/samplechart/0.1.3), in order to execute CNF Cert Suite tests over this Helm chart.

The specific operator and Helm chart that are deployed depend on the `tnf_test_example` DCI component used. Currently, we support `v0.0.1` (it uses simple-demo-operator is used) and `v0.0.2` (the latest one, where mongodb-enterprise operator is used). By using `dci_components_by_query` variable in your settings file, you can select the component that best suits you.

Note that the component defines some data that is used by the hooks. Here you have an [example](https://www.distributed-ci.io/topics/818491de-8ee6-4ae8-a9bc-2d2ce62ef71c/components/95d2c742-d3a3-4bb5-8b8c-7a9a3243eec7) that you can check. If you click in `Data` > `See content`, you will see a JSON string containing the following variables (which needs to be declared):

* `tnf_app_image`: image to be used in the pods under test. In our case, the specification, obtained from [this repository](https://github.com/test-network-function/cnf-certification-test-partner), is a suitable one for passing all the test suites from the CNF Test Suite.
* `tnf_operator_to_install`: information related to the operator to be installed. It must include the following variables within it:
  * `operator_name`: name of the operator.
  * `operator_version`: version of the operator.
  * `operator_bundle`: bundle Image SHA of the operator to be installed. This is used to create a custom catalog for disconnected environments.
* `tnf_helm_chart_to_install`: information related to the Helm chart to be deployed. It must include the following variables within it:
  * `chart_url`: URL to the chart.tgz file that includes the Helm chart.
  * `image_repository`: public image used within the Helm chart.
  * `app_version`: (only needed in disconnected environments) version linked to `image_repository` image, so that the image would be `image_repository`:`app_version`.

These resources create services in the namespace that are updated to `PreferDualStack` IP family policy, then obtaining an IPv6 IP address if the OCP cluster is configured in dual-stack mode.

Example of values for these variables are the following (for connected environments; in disconnected, `tnf_app_image` must point to a private registry):

```yaml
tnf_app_image: quay.io/testnetworkfunction/cnf-test-partner:latest
tnf_operator_to_install:
  operator_name: mongodb-enterprise
  operator_version: v1.17.0
  operator_bundle: registry.connect.redhat.com/mongodb/enterprise-operator-bundle@sha256:f2127ed11f4fb714f5c35f0cc4561da00181ffb5edb098556df598d3a5a6a691
tnf_helm_chart_to_install:
  chart_url: https://github.com/openshift-helm-charts/charts/releases/download/fredco-samplechart-0.1.3/fredco-samplechart-0.1.3.tgz
  image_repository: registry.access.redhat.com/ubi8/nginx-118
  app_version: 1-42
```

For further information, you can check the following blog posts:

- [Running CNF Cert Suite certification with dci-openshift-app-agent](https://blog.distributed-ci.io/cnf-cert-suite-with-dci-openshift-app-agent.html)
- [How to automate DCI components creation](https://blog.distributed-ci.io/automate-dci-components.html)

> Note that, in case you are not using components, operator and Helm chart will not be tested, but you can still run the job. For this, you need to define `tnf_app_image` explicitly in your settings or pipelines, else the job will fail in pre-run stage.
