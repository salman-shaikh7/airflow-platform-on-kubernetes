# Operations Quick Reference

Quick commands for operating the local Kubernetes and Airflow environment.

## Start the Kubernetes VMs

```bash
virsh start k8s-control-plane
virsh start k8s-worker-1
virsh start k8s-worker-2
```

Starting all three with one command:

```bash
for vm in k8s-control-plane k8s-worker-1 k8s-worker-2; do virsh start "$vm"; done
```

`virsh start` may report that a VM is already active. That is harmless.

## Check VM status

Show running VMs:

```bash
virsh list
```

Show all VMs, including stopped ones:

```bash
virsh list --all
```

Check each VM's state:

```bash
for vm in k8s-control-plane k8s-worker-1 k8s-worker-2; do virsh domstate "$vm"; done
```

After starting the VMs, allow Kubernetes a short time to initialize, then check
the nodes:

```bash
kubectl get nodes
```

Expected result: all three nodes eventually show `Ready`.

## Shut down the Kubernetes VMs

Request a graceful shutdown:

```bash
for vm in k8s-worker-1 k8s-worker-2 k8s-control-plane; do virsh shutdown "$vm"; done
```

Confirm they have stopped:

```bash
virsh list --all
```

Wait until each VM shows `shut off`. Avoid `virsh destroy` for normal shutdown;
it is comparable to cutting the power.
