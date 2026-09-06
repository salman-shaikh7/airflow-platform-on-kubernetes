# Operations Quick Reference

Quick commands for operating the local Kubernetes and Airflow environment.

## VM names

| Role | VM name |
|---|---|
| Control plane | `k8s-control-plane` |
| Worker 1 | `k8s-worker-1` |
| Worker 2 | `k8s-worker-2` |

## 1. Start the cluster

### Start all VMs

```bash
for vm in k8s-control-plane k8s-worker-1 k8s-worker-2; do
  virsh start "$vm"
done
```

`virsh start` may report that a VM is already active. That is harmless.

### Start VMs individually

```bash
virsh start k8s-control-plane
virsh start k8s-worker-1
virsh start k8s-worker-2
```

## 2. Check VM status

### Running VMs only

```bash
virsh list
```

### All VMs, including stopped VMs

```bash
virsh list --all
```

### State of each cluster VM

```bash
for vm in k8s-control-plane k8s-worker-1 k8s-worker-2; do
  printf '%-22s ' "$vm"
  virsh domstate "$vm"
done
```

## 3. Verify Kubernetes

The Kubernetes services need a short time to initialize after the VMs start.

```bash
kubectl get nodes
```

Expected state:

```text
k8s-control-plane   Ready
k8s-worker-1        Ready
k8s-worker-2        Ready
```

If the connection is initially refused, wait briefly and run the command again.

## 4. Shut down the cluster

### Request a graceful shutdown

```bash
for vm in k8s-worker-1 k8s-worker-2 k8s-control-plane; do
  virsh shutdown "$vm"
done
```

Workers are shut down first and the control plane last.

### Confirm shutdown

```bash
virsh list --all
```

Wait until all three VMs show `shut off`.

> Avoid `virsh destroy` during normal operation. It is comparable to cutting
> the power rather than performing a graceful shutdown.

## Kubernetes commands

Use these commands in order when you want to understand what is running in an
unfamiliar Kubernetes cluster.

### 1. Select and confirm the cluster context

List all contexts configured in kubeconfig:

```bash
kubectl config get-contexts
```

The `*` in the `CURRENT` column identifies the active context.

Show only the current context:

```bash
kubectl config current-context
```

Switch to another context by replacing `<context-name>`:

```bash
kubectl config use-context <context-name>
```

For example:

```bash
kubectl config use-context kubernetes-admin@kubernetes
```

Changing context determines which cluster and credentials subsequent `kubectl`
commands use. Confirm access to the selected cluster:

```bash
kubectl cluster-info
```

### 2. Inspect the nodes

Start by checking which machines belong to the cluster and whether they are
healthy:

```bash
kubectl get nodes -o wide
```

For detailed health, capacity, labels, taints, and recent node events:

```bash
kubectl describe node <node-name>
```

### 3. List the namespaces

Namespaces divide cluster resources into logical groups:

```bash
kubectl get namespaces
```

### 4. Get a quick cluster-wide overview

Show common resources across every namespace:

```bash
kubectl get all --all-namespaces
```

`kubectl get all` is a convenient overview, but it does not literally include
every Kubernetes resource type. The next commands inspect each important area.

### 5. Inspect workloads

See all pods, their status, IP address, and assigned node:

```bash
kubectl get pods --all-namespaces -o wide
```

See the controllers that create and manage pods:

```bash
kubectl get deployments,statefulsets,daemonsets --all-namespaces
```

See scheduled and completed workloads:

```bash
kubectl get jobs,cronjobs --all-namespaces
```

Inspect only one namespace by replacing `<namespace>`:

```bash
kubectl get all -n <namespace>
```

### 6. Inspect networking

Services provide stable access to pods, while Ingress resources expose HTTP or
HTTPS routes:

```bash
kubectl get services --all-namespaces
kubectl get ingress --all-namespaces
```

### 7. Inspect storage

```bash
kubectl get storageclass
kubectl get persistentvolume
kubectl get persistentvolumeclaim --all-namespaces
```

- `StorageClass` describes how storage is provisioned.
- `PersistentVolume` represents the available or allocated storage.
- `PersistentVolumeClaim` represents a workload's request for storage.

### 8. Check recent cluster events

Events often reveal scheduling failures, image-pull errors, failed health
checks, and storage problems:

```bash
kubectl get events --all-namespaces --sort-by='.metadata.creationTimestamp'
```

### 9. Check CPU and memory usage

These commands work when Kubernetes Metrics Server is installed:

```bash
kubectl top nodes
kubectl top pods --all-namespaces
```

### 10. Investigate a specific resource

After the overview identifies a problem, inspect that resource in detail.

Inspect pod configuration, status, and events:

```bash
kubectl describe pod <pod-name> -n <namespace>
```

List the containers inside a pod:

```bash
kubectl get pod <pod-name> -n <namespace> \
  -o jsonpath='{.spec.containers[*].name}{"\n"}'
```

Read logs from a single-container pod:

```bash
kubectl logs <pod-name> -n <namespace> --tail=100
```

Read logs from a particular container:

```bash
kubectl logs <pod-name> -n <namespace> -c <container-name> --tail=100
```

Follow new log messages; press `Ctrl+C` to stop:

```bash
kubectl logs <pod-name> -n <namespace> -c <container-name> --follow
```

Read logs from the previous crashed container instance:

```bash
kubectl logs <pod-name> -n <namespace> -c <container-name> --previous --tail=100
```
