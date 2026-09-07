# Observability with Prometheus and Grafana

Prometheus collects metrics and Grafana visualizes them. The lab installation
uses conservative resource limits because the VM nodes are small.

## Components

- Prometheus server: stores and queries time-series metrics.
- Node Exporter: exposes node CPU, memory, disk, and network metrics.
- kube-state-metrics: exposes Kubernetes object state.
- Airflow StatsD exporter: exposes Airflow scheduler, DAG, and task metrics.
- Grafana: queries Prometheus and provides dashboards.

Alertmanager and Pushgateway are disabled for this initial lab setup.

## Access

Prometheus is available through the Envoy Gateway at `http://prometheus.local`
when configured, or temporarily with:

```bash
kubectl port-forward service/prometheus-server 9090:80 -n monitoring
```

Grafana is available through the Envoy Gateway at:

```text
http://grafana.local
```

## Validation

In Grafana Explore, query:

```promql
up
```

Airflow metrics can be checked with:

```promql
count({__name__=~"airflow_.*"})
```

The initial dashboard contains scheduler heartbeat, node CPU, node memory,
pod restarts, running pods, task failures, DAG failures, and node disk usage.
