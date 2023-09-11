# Control Plane example

This example creates a deployment with a pod from a web server image and validates if the pods are running.
The deployment uses anti-affinity and replicas, also a service and route are created to access the web service.
This example can also be installed with Helm by setting the correct variable (see bellow).

The table below shows the available variables and their default values.

| Name                        | Default                                              | Description                                                      |
|-----------------------------|------------------------------------------------------|------------------------------------------------------------------|
| openshift\_app\_ns          | myns                                                 | Name of the NS to use                                            |
| openshift\_app\_replicas    | 3                                                    | Number of pod replicas to deploy with anti-affinity rule         |
| openshift\_app\_image       | mirror.gcr.io/kennethreitz/httpbin:latest            | Name of the image to use for the web server pod                  |
| openshift\_app\_cmds        | [gunicorn, -b, "[::]:8080", httpbin:app, -k, gevent] | A list of commands to pass to the web server pod                 |
| openshift\_app\_registry    | defined in disconnected envs                         | Name of the registry to use to pull web server image             |
| pullsecret\_tmp\_file       | Provided by the agent if none defined                | Only for disconnected envs, path where the pullsecret is located |
| openshift\_app\_helm\_chart | null                                                 | [Optional] when defined, uses this path as the chart reference   |

## Requirements

- Namespace needs to be created before launching this app.
- Pull secret for disconnected environments.
