# Step 3: Helm Installation

Installation date: 2026-09-03

## Objective

Install Helm on the local laptop so it can manage application releases in the
remote Kubernetes cluster.

Helm is not installed on the control-plane or worker nodes. Like `kubectl`, the
local Helm client reads the configured kubeconfig and communicates with the
Kubernetes API server.

```text
Helm on laptop
      |
      | uses kubeconfig
      v
Kubernetes API server
      |
      v
Resources inside the cluster
```

## Installation

The official Helm 3 installation script was downloaded and executed:

```bash
cd /tmp &&
curl -fsSLo get_helm.sh https://raw.githubusercontent.com/helm/helm/main/scripts/get-helm-3 &&
chmod 700 get_helm.sh &&
./get_helm.sh &&
helm version --short
```

The installer downloaded the release archive, verified its checksum, and
installed the Helm binary at:

```text
/usr/local/bin/helm
```

## Result

Installed version:

```text
v3.21.4+g813176c
```

Status: **Installed successfully**

This version satisfies the Apache Airflow Helm chart requirement of Helm
`v3.19.0` or newer.

## Verification commands

Display the local Helm client version:

```bash
helm version --short
```

Confirm Helm can communicate with the configured Kubernetes cluster and list
all existing releases:

```bash
helm list --all-namespaces
```

An empty release list is expected before the first Helm-managed application is
installed.

## Reference

- [Official Helm installation documentation](https://helm.sh/docs/intro/install/)
