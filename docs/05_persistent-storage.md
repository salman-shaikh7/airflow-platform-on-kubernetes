# Step 5: Configure and Test Persistent Storage

Completion date: 2026-09-05

## Goal

Install Rancher Local Path Provisioner and confirm that data survives Pod
deletion and recreation.

Local-path storage is suitable for this lab, but it remains tied to one worker
node and is not highly available.

## Install the provisioner

Create the directory and download the pinned `v0.0.36` manifest:

```bash
mkdir -p kubernetes/storage

curl -fLo kubernetes/storage/local-path-provisioner.yaml \
  https://raw.githubusercontent.com/rancher/local-path-provisioner/v0.0.36/deploy/local-path-storage.yaml
```

The manifest creates the namespace, permissions, provisioner Deployment,
StorageClass, and configuration required for dynamic local volumes.

We added resource controls to the provisioner container:

```yaml
resources:
  requests:
    cpu: 25m
    memory: 32Mi
  limits:
    cpu: 200m
    memory: 128Mi
```

Apply it and wait for the Deployment:

```bash
kubectl apply -f kubernetes/storage/local-path-provisioner.yaml

kubectl rollout status deployment/local-path-provisioner \
  -n local-path-storage
```

Observed result:

```text
deployment "local-path-provisioner" successfully rolled out
```

## Verify storage infrastructure

```bash
kubectl get pods -n local-path-storage
kubectl get storageclass
```

Relevant output:

```text
NAME                              READY   STATUS
local-path-provisioner-<pod-id>   1/1     Running
```

```text
NAME         PROVISIONER             RECLAIMPOLICY   VOLUMEBINDINGMODE
local-path   rancher.io/local-path   Delete          WaitForFirstConsumer
```

- `Delete`: deleting the PVC also deletes its PV and stored data.
- `WaitForFirstConsumer`: Kubernetes waits for a Pod before selecting the
  storage node.
- The class is not default; workloads must explicitly request `local-path`.
- Data is stored under `/opt/local-path-provisioner` on the selected node.

## Test a PVC and Pod

The test manifest at `kubernetes/storage/storage-test.yaml` creates:

- Namespace `storage-test`
- PVC `local-path-test-pvc`, requesting `100Mi` with `ReadWriteOnce`
- BusyBox Pod mounting the PVC at `/data`

Apply and inspect it:

```bash
kubectl apply -f kubernetes/storage/storage-test.yaml
kubectl get pods -n storage-test
kubectl get pvc -n storage-test -o wide
```

Observed result:

```text
NAME               READY   STATUS
storage-test-pod   1/1     Running
```

```text
NAME                  STATUS   CAPACITY   ACCESS MODES   STORAGECLASS
local-path-test-pvc   Bound    100Mi      RWO            local-path
```

`Bound` means the PVC is connected to a PV. To see which Pod references it:

```bash
kubectl describe pvc local-path-test-pvc -n storage-test
```

Expected field:

```text
Used By: storage-test-pod
```

## Prove persistence

Write and read a file:

```bash
kubectl exec -n storage-test storage-test-pod -- \
  sh -c 'echo "persistent storage works" > /data/test.txt'

kubectl exec -n storage-test storage-test-pod -- cat /data/test.txt
```

Output:

```text
persistent storage works
```

Delete only the Pod and confirm the PVC remains:

```bash
kubectl delete pod storage-test-pod -n storage-test
kubectl get pod,pvc -n storage-test
```

Recreate the Pod and read the same file:

```bash
kubectl apply -f kubernetes/storage/storage-test.yaml

kubectl wait --for=condition=Ready pod/storage-test-pod \
  -n storage-test --timeout=60s

kubectl exec -n storage-test storage-test-pod -- cat /data/test.txt
```

The output remained:

```text
persistent storage works
```

This confirms the recreated Pod mounted the same persistent volume.

## Cleanup

Remove only the temporary test resources:

```bash
kubectl delete -f kubernetes/storage/storage-test.yaml
```

The test PVC, PV, and data are deleted. The provisioner and `local-path`
StorageClass remain installed for PostgreSQL.

## Result

```text
Pod -> PVC -> local-path StorageClass -> PV -> worker-node directory
```

The cluster can now dynamically provide persistent storage for the bundled
PostgreSQL database used by our first Airflow deployment.

## Reference

- [Rancher Local Path Provisioner](https://github.com/rancher/local-path-provisioner/tree/v0.0.36)
