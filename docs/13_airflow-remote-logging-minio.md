# Airflow remote task logging with MinIO

Airflow task logs are stored in an S3-compatible MinIO bucket instead of
depending on the temporary KubernetesExecutor task pod.

## Components

- MinIO StatefulSet with one replica.
- `local-path` PVC (`minio-data`, 3Gi) mounted at `/data`.
- Internal Service `minio.minio.svc.cluster.local:9000`.
- `airflow-logs` bucket created by a one-time Job.
- Airflow Secret `airflow-minio-connection` containing `AIRFLOW_CONN_MINIO_S3`.

## Airflow configuration

```yaml
extraEnvFrom: |
  - secretRef:
      name: airflow-minio-connection

config:
  logging:
    remote_logging: "True"
    remote_base_log_folder: "s3://airflow-logs"
    remote_log_conn_id: "minio_s3"
    delete_local_logs: "False"

apiServer:
  allowPodLogReading: false
```

The API server cannot read temporary pod logs; completed-task logs are read
from MinIO. The UI may still attempt its live pod-log path first and show a
harmless `403`, then successfully fall back to the remote object.

## Validation

```bash
kubectl exec deployment/airflow-api-server -n airflow -- \
  airflow config get-value logging remote_logging
kubectl exec deployment/airflow-api-server -n airflow -- \
  airflow config get-value logging remote_base_log_folder
```

Trigger a DAG, wait for success, and confirm the task log source begins with
`s3://airflow-logs/` in the Airflow UI.

This single-node MinIO setup is suitable for the lab. Its data is tied to one
worker's local disk; production should use managed S3/Blob/GCS or distributed,
redundant object storage.
