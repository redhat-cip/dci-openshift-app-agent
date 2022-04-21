This example deploys a couple of pods in two different namespaces, to be used with the CNF Test Suite provided by [test-network-function](https://github.com/test-network-function/test-network-function) in a multi-namespace scenario.

The Deployment specification of this pod, obtained from [this repository](https://github.com/test-network-function/cnf-certification-test-partner/blob/main/local-test-infra/local-pod-under-test.yaml), is a suitable one for passing all the test suites from the CNF Test Suite.

It also deploys an operator in one of the namespaces, based on [simple-demo-operator-bundle](https://quay.io/repository/opdev/simple-demo-operator-bundle), in order to execute CNF Cert Suite and Preflight tests over this operator.
