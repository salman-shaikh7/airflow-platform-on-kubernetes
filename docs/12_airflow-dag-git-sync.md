# Airflow DAG delivery with Git sync

Airflow components use the Git sync sidecar/init container to copy DAG files
from the repository into the shared DAGs directory. With KubernetesExecutor,
the scheduler and task-related components receive the same DAG bundle.

## Configuration

In `helm/airflow-values.yaml`:

```yaml
dags:
  gitSync:
    enabled: true
    repo: https://github.com/salman-shaikh7/airflow-platform-on-kubernetes.git
    branch: main
    ref: main
    depth: 1
    subPath: dags
    period: 30s
```

`branch` is retained for chart compatibility; `ref` selects the Git revision.
The `subPath` setting tells Git sync to use only the repository's `dags/`
directory.

## Validation

```bash
kubectl get pods -n airflow
kubectl logs -n airflow deployment/airflow-dag-processor -c git-sync --tail=100
```

The DAG should appear in the Airflow UI after the sync interval. A common
failure is a nonexistent branch or ref, which leaves `git-sync-init` in
`CrashLoopBackOff`.
