# TNF Test example

This example deploys a couple of pods in two different namespaces, to be used with the CNF Test Suite provided by [test-network-function](https://github.com/test-network-function/cnf-certification-test) in a multi-namespace scenario.

The StatefulSet specification of this pod, obtained from [this repository](https://github.com/test-network-function/cnf-certification-test-partner), is a suitable one for passing all the test suites from the CNF Test Suite.

Other resources are also deployed:

- Resource quota, extracted from [this repository](https://github.com/test-network-function/cnf-certification-test-partner/blob/main/test-target/resource-quota.yaml).
- Network policies, extracted from these sources: [(1)](https://github.com/test-network-function/cnf-certification-test-partner/blob/main/test-target/ingress-deny-all-np.yaml), [(2)](https://github.com/test-network-function/cnf-certification-test-partner/blob/main/test-target/egress-deny-all-np.yaml) and [(3)](https://github.com/test-network-function/cnf-certification-test-partner/blob/main/test-target/pod-to-pod-np.yaml).
- CRD under test, extracted from [this repository](https://github.com/test-network-function/cnf-certification-test-partner/blob/main/test-target/local-crd-under-test.yaml).
- Pod disruption budget, extracted from [this repository](https://github.com/test-network-function/cnf-certification-test-partner/blob/main/test-target/pod-disruption-budget.yaml).

Finally, it also deploys an operator in one of the namespaces, based on [simple-demo-operator-bundle](https://quay.io/repository/opdev/simple-demo-operator-bundle), in order to execute CNF Cert Suite and Preflight tests over this operator.
