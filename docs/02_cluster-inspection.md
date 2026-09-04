# Step 2: Initial Kubernetes Cluster Inspection

Inspection date: 2026-09-03

## Objective

Validate that the Kubernetes cluster is reachable and healthy, understand its
available capacity, and identify prerequisites for deploying Airflow.

## 1. Connection and versions

Commands:

```bash
kubectl config current-context
kubectl cluster-info
kubectl version
```

Results:

- Active context: `kubernetes-admin@kubernetes`
- Kubernetes API: `https://192.168.122.131:6443`
- CoreDNS is reachable through the Kubernetes API.
- kubectl client: `v1.36.3`
- Kubernetes server: `v1.34.11`
- Kustomize: `v5.8.1`

Status: **Connected**

Note: The client is two minor versions newer than the server, which exceeds
the supported `kubectl` version skew of one minor version. We should install a
`kubectl` version compatible with Kubernetes `v1.34` before relying on this
setup for ongoing administration.

Resolution: Completed in
[Step 4: Align the kubectl client version](04_kubectl-version-alignment.md).

## 2. Node health

Commands:

```bash
kubectl get nodes -o wide

kubectl get nodes \
  -o custom-columns='NAME:.metadata.name,CPU:.status.capacity.cpu,MEMORY:.status.capacity.memory,PODS:.status.capacity.pods'

kubectl get nodes \
  -o custom-columns='NAME:.metadata.name,CPU:.status.allocatable.cpu,MEMORY:.status.allocatable.memory,PODS:.status.allocatable.pods'
```

Results:

| Node | Role | Status | CPU | Allocatable memory | Pod limit | IP |
|---|---|---:|---:|---:|---:|---|
| `k8s-control-plane` | Control plane | Ready | 2 | 2,875,268 Ki | 110 | `192.168.122.131` |
| `k8s-worker-1` | Worker | Ready | 2 | 2,875,268 Ki | 110 | `192.168.122.94` |
| `k8s-worker-2` | Worker | Ready | 2 | 2,875,276 Ki | 110 | `192.168.122.38` |

All nodes run:

- Kubernetes `v1.34.11`
- Ubuntu `24.04.4 LTS`
- containerd `2.2.1`

Cluster capacity is approximately 6 CPUs and 8.2 GiB of allocatable memory.
Airflow will need a lightweight configuration with conservative resource
requests.

Status: **All three nodes are Ready**

## 3. System workload health

Commands:

```bash
kubectl get pods --all-namespaces

kubectl get pods --all-namespaces \
  --field-selector=status.phase!=Running,status.phase!=Succeeded
```

Results:

- Kubernetes control-plane components are running.
- Both CoreDNS pods are running.
- Calico networking components are running.
- No failed, pending, or otherwise unhealthy pods were found.
- Existing restart counts correspond with the virtual machines being
  restarted.

Status: **Healthy**

## 4. Persistent storage

Commands:

```bash
kubectl get storageclass
kubectl get persistentvolumes
kubectl get persistentvolumeclaims --all-namespaces
```

Results:

- No StorageClass exists.
- No PersistentVolumes exist.
- No PersistentVolumeClaims exist.

Status: **Storage provisioning is not configured**

Airflow's PostgreSQL database needs persistent storage. Before installing
Airflow, we must configure a storage solution or deliberately use temporary
storage for an initial disposable experiment.

## 5. Helm

Commands:

```bash
helm version --short
helm list --all-namespaces
```

Result:

```text
helm: command not found
```

Status: **Helm must be installed**

## 6. Resource metrics

Commands:

```bash
kubectl top nodes
kubectl top pods --all-namespaces
```

Result:

```text
Metrics API not available
```

Status: **Metrics Server is not installed**

Metrics Server is useful for observing current CPU and memory usage and is
required for metrics-based autoscaling. It is not required for the first
Airflow installation.

## Overall assessment

The Kubernetes control plane, worker nodes, networking, DNS, and remote
`kubectl` connection are healthy.

Before deploying Airflow:

1. Install Helm.
2. Configure persistent storage.
3. Align the local `kubectl` client with the Kubernetes server version.

Helm installation and `kubectl` alignment were completed after this initial
inspection. Persistent storage remains to be configured.

Optional improvement:

4. Install Metrics Server for resource usage reporting.
