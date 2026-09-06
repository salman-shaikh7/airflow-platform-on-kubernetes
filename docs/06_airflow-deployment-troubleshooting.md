# Step 6: Deploy and troubleshoot Airflow

## Outcome

Apache Airflow Helm chart `1.22.0` was deployed with `KubernetesExecutor`.
PostgreSQL uses the `local-path` StorageClass, all active Airflow pods are
healthy, and the UI is accessible from the laptop.

## Install or upgrade

```bash
helm upgrade --install airflow apache-airflow/airflow \
  --version 1.22.0 \
  --namespace airflow \
  --values helm/airflow-values.yaml \
  --values helm/airflow-secrets-values.yaml
```

We intentionally omitted `--wait`: the chart's migration and user-creation
Jobs use Helm hooks, and using `--wait` prevented migrations from running at
the required time. The Airflow pods then remained in their
`wait-for-airflow-migrations` init containers.

## Problems encountered and fixes

| Symptom | Cause | Fix |
|---|---|---|
| Pods were `Evicted` and nodes reported `DiskPressure` | VM root logical volumes used only half of their available LVM space | Extended each root LV/filesystem and waited for `DiskPressure=False` |
| Triggerer PVC remained `Pending` | Triggerer log persistence requested storage without a StorageClass | Disabled triggerer persistence for this lab; PostgreSQL persistence remains enabled |
| Components waited indefinitely for migrations | The migration Helm hook did not run while installing with `--wait` | Re-ran the Helm upgrade without `--wait` |
| Triggerer, scheduler and DAG processor were `OOMKilled` | Initial memory limits were too small | Increased component requests and limits in `helm/airflow-values.yaml` |
| Scheduler startup probe restarted a working scheduler | Scheduler startup and heartbeat checks were slow on the small VMs | Allowed more CPU and increased the startup-probe grace period |

Old `Evicted`, failed, and completed pod objects were removed only after their
healthy replacements were verified.

## Verification

```bash
kubectl get nodes
kubectl get pvc -n airflow
kubectl get pods -n airflow \
  --field-selector=status.phase!=Failed,status.phase!=Succeeded
```

Expected active components:

```text
airflow-api-server     Running
airflow-dag-processor  Running
airflow-postgresql     Running
airflow-scheduler      Running
airflow-statsd         Running
airflow-triggerer      Running
```

## Access the UI

```bash
kubectl port-forward service/airflow-api-server 8080:8080 -n airflow
```

Open <http://localhost:8080>. The port-forward command must remain running.
Credentials are stored only in the ignored `helm/airflow-secrets-values.yaml`
file and must never be committed.

