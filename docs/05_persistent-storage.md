# Step 5: Configure and Test Persistent Storage

Completion date: 2026-09-05

## Objective

Install Rancher Local Path Provisioner, create the `local-path` StorageClass,
and prove that data survives deletion and recreation of a Pod.

Local Path Provisioner is suitable for this lab. Its volumes are stored on one
Kubernetes node and are not highly available across nodes.

## 1. Create the local manifest directory

Command:

```bash
cd "$HOME/Desktop/airflow-platform-on-kubernetes" &&
mkdir -p kubernetes/storage
```

Verify:

```bash
ls -ld kubernetes/storage
```

Example output:

```text
drwxrwxr-x 3 sal sal 4096 Sep 5 14:46 kubernetes/storage
```

## 2. Download the pinned provisioner manifest

Command:

```bash
curl -fLo kubernetes/storage/local-path-provisioner.yaml \
  https://raw.githubusercontent.com/rancher/local-path-provisioner/v0.0.36/deploy/local-path-storage.yaml
```

Verify:

```bash
ls -lh kubernetes/storage/local-path-provisioner.yaml
```

The release is pinned to `v0.0.36` so the manifest does not change
unexpectedly between installations.

The manifest creates:

| Resource | Purpose |
|---|---|
| Namespace | Isolates the provisioner's resources in `local-path-storage`. |
| ServiceAccount | Gives the provisioner a Kubernetes identity. |
| Role and ClusterRole | Allow it to inspect PVCs and nodes and manage PVs and helper Pods. |
| RoleBindings | Assign those permissions to its ServiceAccount. |
| Deployment | Runs the Local Path Provisioner controller. |
| StorageClass | Provides dynamic storage using the name `local-path`. |
| ConfigMap | Defines the node path and setup/teardown scripts. |

By default, provisioned data is stored under this path on the selected node:

```text
/opt/local-path-provisioner
```

## 3. Configure provisioner resources

The downloaded Deployment did not specify CPU or memory resources. The
following configuration was added to its container:

```yaml
resources:
  requests:
    cpu: 25m
    memory: 32Mi
  limits:
    cpu: 200m
    memory: 128Mi
```

The requests reserve scheduling capacity. Actual usage can be lower. CPU use
above `200m` is throttled, while memory use above `128Mi` can result in an
`OOMKilled` container.

## 4. Install the provisioner

Command:

```bash
kubectl apply -f kubernetes/storage/local-path-provisioner.yaml
```

Representative first-install output:

```text
namespace/local-path-storage created
serviceaccount/local-path-provisioner-service-account created
role.rbac.authorization.k8s.io/local-path-provisioner-role created
clusterrole.rbac.authorization.k8s.io/local-path-provisioner-role created
rolebinding.rbac.authorization.k8s.io/local-path-provisioner-bind created
clusterrolebinding.rbac.authorization.k8s.io/local-path-provisioner-bind created
deployment.apps/local-path-provisioner created
storageclass.storage.k8s.io/local-path created
configmap/local-path-config created
```

After adding resource requests and limits, the same command was applied again.
Kubernetes updated only the changed Deployment and left unchanged resources in
place.

Wait for the updated Deployment:

```bash
kubectl rollout status deployment/local-path-provisioner \
  -n local-path-storage
```

Observed output:

```text
deployment "local-path-provisioner" successfully rolled out
```

## 5. Verify the provisioner and StorageClass

Commands:

```bash
kubectl get pods -n local-path-storage
kubectl get storageclass
```

Observed state:

```text
NAME                                     READY   STATUS    RESTARTS
local-path-provisioner-<pod-id>          1/1     Running   0
```

```text
NAME         PROVISIONER             RECLAIMPOLICY   VOLUMEBINDINGMODE      ALLOWVOLUMEEXPANSION
local-path   rancher.io/local-path   Delete          WaitForFirstConsumer   false
```

Important properties:

- `Delete`: deleting a PVC also deletes its PV and node data directory.
- `WaitForFirstConsumer`: a volume is created only after a Pod requests the
  PVC and Kubernetes chooses its node.
- `false`: PVC-based volume expansion is not supported by this StorageClass.
- The class is not marked as default; workloads must explicitly request
  `local-path`.

Verify the provisioner resources:

```bash
kubectl get deployment local-path-provisioner \
  -n local-path-storage \
  -o jsonpath='{.spec.template.spec.containers[0].resources}{"\n"}'
```

Expected values:

```text
map[limits:map[cpu:200m memory:128Mi] requests:map[cpu:25m memory:32Mi]]
```

## 6. Create the storage test manifest

File:

```text
kubernetes/storage/storage-test.yaml
```

Contents:

```yaml
apiVersion: v1
kind: Namespace
metadata:
  name: storage-test

---
apiVersion: v1
kind: PersistentVolumeClaim
metadata:
  name: local-path-test-pvc
  namespace: storage-test
spec:
  accessModes:
    - ReadWriteOnce
  storageClassName: local-path
  resources:
    requests:
      storage: 100Mi

---
apiVersion: v1
kind: Pod
metadata:
  name: storage-test-pod
  namespace: storage-test
spec:
  containers:
    - name: storage-test
      image: busybox:1.37
      resources:
        requests:
          cpu: 10m
          memory: 16Mi
        limits:
          cpu: 100m
          memory: 64Mi
      command: ["sh", "-c", "sleep 3600"]
      volumeMounts:
        - name: test-volume
          mountPath: /data
  volumes:
    - name: test-volume
      persistentVolumeClaim:
        claimName: local-path-test-pvc
```

The PVC requests `100Mi` using `local-path`. The Pod mounts that claim at
`/data`.

## 7. Create and inspect the test resources

Apply the manifest:

```bash
kubectl apply -f kubernetes/storage/storage-test.yaml
```

Observed output after the namespace and PVC already existed:

```text
namespace/storage-test unchanged
persistentvolumeclaim/local-path-test-pvc unchanged
pod/storage-test-pod created
```

Check the Pod:

```bash
kubectl get pods -n storage-test
```

Observed output:

```text
NAME               READY   STATUS    RESTARTS
storage-test-pod   1/1     Running   0
```

Check the PVC:

```bash
kubectl get pvc -n storage-test -o wide
```

Observed output:

```text
NAME                  STATUS   VOLUME                                     CAPACITY   ACCESS MODES   STORAGECLASS   VOLUMEMODE
local-path-test-pvc   Bound    pvc-01aba6fd-7abe-40e5-b365-fe281d65eabc   100Mi      RWO            local-path     Filesystem
```

`Bound` means the PVC is connected to a PersistentVolume. It does not, by
itself, mean a Pod is currently mounting the claim.

Check which Pod uses the PVC:

```bash
kubectl describe pvc local-path-test-pvc -n storage-test
```

Expected relevant field:

```text
Used By: storage-test-pod
```

Check the volume and container mount:

```bash
kubectl describe pod storage-test-pod -n storage-test
```

Expected relevant fields:

```text
Mounts:
  /data from test-volume

Volumes:
  test-volume:
    Type:       PersistentVolumeClaim
    ClaimName:  local-path-test-pvc
```

## 8. Write data to the volume

Write a file:

```bash
kubectl exec -n storage-test storage-test-pod -- \
  sh -c 'echo "persistent storage works" > /data/test.txt'
```

Read the file:

```bash
kubectl exec -n storage-test storage-test-pod -- \
  cat /data/test.txt
```

Observed output:

```text
persistent storage works
```

## 9. Prove that data survives Pod deletion

Delete only the Pod:

```bash
kubectl delete pod storage-test-pod -n storage-test
```

Confirm the PVC remains bound:

```bash
kubectl get pod,pvc -n storage-test
```

Observed state:

```text
NAME                                        STATUS   CAPACITY   ACCESS MODES   STORAGECLASS
persistentvolumeclaim/local-path-test-pvc   Bound    100Mi      RWO            local-path
```

Recreate the Pod:

```bash
kubectl apply -f kubernetes/storage/storage-test.yaml
```

Wait for it:

```bash
kubectl wait --for=condition=Ready pod/storage-test-pod \
  -n storage-test --timeout=60s
```

Expected output:

```text
pod/storage-test-pod condition met
```

Read the file from the recreated Pod:

```bash
kubectl exec -n storage-test storage-test-pod -- \
  cat /data/test.txt
```

Observed output:

```text
persistent storage works
```

This proves that deleting the Pod did not delete the data. The recreated Pod
used the same PVC and mounted the same PersistentVolume.

## 10. Test conclusion

The complete storage path works:

```text
Pod
  -> PersistentVolumeClaim
  -> local-path StorageClass
  -> Local Path Provisioner
  -> PersistentVolume
  -> directory on the selected worker node
```

The provisioner is ready to supply persistent storage to the bundled
PostgreSQL instance used by the first Airflow deployment.

## 11. Cleanup after testing

The test resources can be removed after the test is complete:

```bash
kubectl delete -f kubernetes/storage/storage-test.yaml
```

Because the StorageClass uses `reclaimPolicy: Delete`, removing the test PVC
also removes its PV and test data. The Local Path Provisioner itself remains
installed.

Verify cleanup:

```bash
kubectl get namespace storage-test
kubectl get pv
kubectl get storageclass local-path
```

Expected result:

- The `storage-test` namespace is not found.
- The test PV is gone.
- The `local-path` StorageClass still exists.

## Reference

- [Rancher Local Path Provisioner](https://github.com/rancher/local-path-provisioner/tree/v0.0.36)
