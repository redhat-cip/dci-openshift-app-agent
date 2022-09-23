# TNF Test example

This example deploys a couple of pods in two different namespaces, to be used with the CNF Test Suite provided by [test-network-function](https://github.com/test-network-function/cnf-certification-test) in a multi-namespace scenario.

The specification of this pod, obtained from [this repository](https://github.com/test-network-function/cnf-certification-test-partner), is a suitable one for passing all the test suites from the CNF Test Suite.

In particular, two namespaces are created, called `test-cnf` and `production-cnf`, mimic-ing the two typical environments we can find to deploy application workloads. In the first case, a Deployment is used to create the pods, and in the second case, it is used a StatefulSet.

Other resources related to the pods under test are also deployed:

- Local StorageClass and PersistentVolumes, attached to the pods under test in `production-cnf` namespace.
- Resource quotas, extracted from [this repository](https://github.com/test-network-function/cnf-certification-test-partner/blob/main/test-target/resource-quota.yaml).
- Network policies, extracted from these sources: [(1)](https://github.com/test-network-function/cnf-certification-test-partner/blob/main/test-target/ingress-deny-all-np.yaml), [(2)](https://github.com/test-network-function/cnf-certification-test-partner/blob/main/test-target/egress-deny-all-np.yaml) and [(3)](https://github.com/test-network-function/cnf-certification-test-partner/blob/main/test-target/pod-to-pod-np.yaml).
- CRD under test, extracted from [this repository](https://github.com/test-network-function/cnf-certification-test-partner/blob/main/test-target/local-crd-under-test.yaml).
- Pod disruption budget, extracted from [this repository](https://github.com/test-network-function/cnf-certification-test-partner/blob/main/test-target/pod-disruption-budget.yaml).
- Hugepages configuration in the pods under test, extracted from [this repository](https://github.com/test-network-function/cnf-certification-test-partner/tree/main/examples/platform).
  - Note that, to use this feature, you need to activate `tnf_enable_hugepages: true` in your code (default to `false`).
- Affinity rules applied to the pods under test. In the case of `test-cnf` namespace, pods are deployed using `podAffinity` rule to keep the pods in the same worker node, also using `AffinityRequired: 'true'` label, and in `production-cnf` namespace, a `podAntiAffinity` rule is used to deploy the pods in different worker nodes.
- Pods in `test-cnf` namespace are deployed with non-guaranteed QoS, whereas pods in `production-cnf` are deployed with guaranteed QoS, together with certain CPU allocation constraints and runtime class definition.

Finally, apart from the pods under test, it also deploys, in one of the namespaces:

- An operator, based on [mongodb-enterprise](https://catalog.redhat.com/software/operators/detail/5e9872923f398525a0ceafba), in order to execute CNF Cert Suite and Preflight tests over this operator.
- A Helm chart, based on [fredco samplechart](https://github.com/openshift-helm-charts/charts/tree/main/charts/partners/fredco/samplechart/0.1.3), in order to execute CNF Cert Suite tests over this Helm chart.

These two last resources need the following variables to be declared:

* `tnf_operator_to_install`: information related to the operator to be installed. It must include the following variables within it:
  * `operator_name`: name of the operator.
  * `operator_version`: version of the operator.
  * `operator_bundle`: bundle Image SHA of the operator to be installed. This is used to create a custom catalog for disconnected environments.

* `tnf_helm_chart_to_install`: information related to the Helm chart to be deployed. It must include the following variables within it:
  * `chart_url`: URL to the chart.tgz file that includes the Helm chart.
  * `image_repository`: public image used within the Helm chart.
  * `app_version`: (only needed in disconnected environments) version linked to `image_repository` image, so that the image would be `image_repository`:`app_version`.

Example of values for these variables are the following (in fact, these are the default values):

```yaml
tnf_operator_to_install:
  operator_name: mongodb-enterprise
  operator_version: v1.17.0
  operator_bundle: registry.connect.redhat.com/mongodb/enterprise-operator-bundle@sha256:f2127ed11f4fb714f5c35f0cc4561da00181ffb5edb098556df598d3a5a6a691
tnf_helm_chart_to_install:
  chart_url: https://github.com/openshift-helm-charts/charts/releases/download/fredco-samplechart-0.1.3/fredco-samplechart-0.1.3.tgz
  image_repository: registry.access.redhat.com/ubi8/nginx-118
  app_version: 1-42
```
