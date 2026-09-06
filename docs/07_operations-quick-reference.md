# Operations Quick Reference

## VM cluster lifecycle

VMs: `k8s-control-plane`, `k8s-worker-1`, `k8s-worker-2`

### Start

```bash
for vm in k8s-control-plane k8s-worker-1 k8s-worker-2; do virsh start "$vm"; done
```

### Status

```bash
virsh list --all
```

```bash
kubectl get nodes
```

After startup, wait briefly if the nodes are not immediately `Ready`.

### Shut down

```bash
for vm in k8s-worker-1 k8s-worker-2 k8s-control-plane; do virsh shutdown "$vm"; done
```

```bash
virsh list --all
```

Use `shutdown` for a graceful stop; avoid `virsh destroy` during normal use.

## Inspect a Kubernetes cluster

Run these groups from top to bottom when exploring a cluster.

### 1. Context and connection

```bash
kubectl config get-contexts
```

```bash
kubectl config current-context
```

```bash
kubectl config use-context <context-name>
```

```bash
kubectl cluster-info
```

### 2. Nodes and namespaces

```bash
kubectl get nodes -o wide
```

```bash
kubectl get namespaces
```

### 3. Workloads

```bash
kubectl get pods -A -o wide
```

```bash
kubectl get deployments,statefulsets,daemonsets -A
```

```bash
kubectl get jobs,cronjobs -A
```

```bash
kubectl get all -n <namespace>
```

`kubectl get all -A` is a fast overview, but does not include every resource
type.

#### Pods by status

All existing pods:

```bash
kubectl get pods -A
```

Running:

```bash
kubectl get pods -A --field-selector=status.phase=Running
```

Pending:

```bash
kubectl get pods -A --field-selector=status.phase=Pending
```

Failed, including most evicted pods:

```bash
kubectl get pods -A --field-selector=status.phase=Failed
```

Successfully completed:

```bash
kubectl get pods -A --field-selector=status.phase=Succeeded
```

Non-running:

```bash
kubectl get pods -A --field-selector=status.phase!=Running
```

Active only; exclude succeeded and failed pods:

```bash
kubectl get pods -A --field-selector=status.phase!=Succeeded,status.phase!=Failed
```

Evicted pods (`jq` required):

```bash
kubectl get pods -A -o json | jq -r '.items[] | select(.status.reason == "Evicted") | [.metadata.namespace, .metadata.name] | @tsv'
```

Terminating pods (`jq` required):

```bash
kubectl get pods -A -o json | jq -r '.items[] | select(.metadata.deletionTimestamp != null) | [.metadata.namespace, .metadata.name] | @tsv'
```

### 4. Networking

```bash
kubectl get services,ingresses -A
```

### 5. Storage

```bash
kubectl get storageclass
```

```bash
kubectl get persistentvolume
```

```bash
kubectl get persistentvolumeclaim -A
```

### 6. Live CPU and memory

```bash
kubectl top nodes
```

```bash
kubectl top pods -A --sort-by=memory
```

```bash
kubectl top pods -A --sort-by=cpu
```

```bash
kubectl top pods -A --containers
```

### 7. Recent events

```bash
kubectl get events -A --sort-by='.metadata.creationTimestamp'
```

## Quick troubleshooting

Replace values inside `<...>`.

Full resource details and events:

```bash
kubectl describe pod <pod-name> -n <namespace>
```

Recent logs:

```bash
kubectl logs <pod-name> -n <namespace> --tail=100
```

Logs for a particular container:

```bash
kubectl logs <pod-name> -n <namespace> -c <container-name> --tail=100
```

Follow logs (`Ctrl+C` to stop):

```bash
kubectl logs <pod-name> -n <namespace> -c <container-name> --follow
```

Logs from the previous crashed container:

```bash
kubectl logs <pod-name> -n <namespace> -c <container-name> --previous --tail=100
```
