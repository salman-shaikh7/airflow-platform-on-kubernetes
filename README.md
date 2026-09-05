# Airflow Platform

A hands-on learning project for deploying and operating Apache Airflow on a
local multi-node Kubernetes cluster.

## Initial goals

- Learn Kubernetes through practical exercises.
- Deploy Airflow to the cluster.
- Understand the main Airflow and Kubernetes components.
- Document the setup and decisions as the project develops.

## Documentation

- [Initial Airflow deployment plan](docs/00_plan_v1.md)
- [Step 1: Configure access to the Kubernetes cluster](docs/01_kubernetes-cluster-access.md)
- [Step 2: Inspect the Kubernetes cluster](docs/02_cluster-inspection.md)
- [Step 3: Install Helm](docs/03_helm-installation.md)
- [Step 4: Align the kubectl client version](docs/04_kubectl-version-alignment.md)
- [Step 5: Configure and test persistent storage](docs/05_persistent-storage.md)

## Status

The Kubernetes cluster is running and can be accessed from the local machine
using both `kubectl` and the VS Code Kubernetes extension.
