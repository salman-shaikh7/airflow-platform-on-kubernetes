# Airflow on Kubernetes: Initial Plan

We will deploy Airflow using the official Apache Airflow Helm chart. Helm lets
us configure a complex application through one `values.yaml` file while still
creating standard Kubernetes resources underneath.

## Deployment path

### 1. Inspect cluster capacity

- Check the Kubernetes version.
- Check the CPU and memory available on each node.
- Inspect the available storage classes.
- Check whether Helm is installed.

### 2. Create an Airflow namespace

Create a dedicated `airflow` namespace to keep Airflow resources isolated from
other applications in the cluster.

### 3. Prepare Helm

- Install Helm if needed.
- Add the official Apache Airflow chart repository.

### 4. Create our configuration

- Add `helm/airflow-values.yaml` to Git.
- Begin with a lightweight configuration suitable for three laptop VMs.
- Configure resource requests so Airflow does not overwhelm the cluster.

### 5. Choose the executor

Initially use `KubernetesExecutor`.

The Airflow scheduler will create a temporary Kubernetes pod for each task.
This will help demonstrate the relationship between Airflow tasks and
Kubernetes pods.

### 6. Configure the supporting components

- **PostgreSQL:** stores Airflow metadata.
- **Scheduler:** determines when tasks should run.
- **API server and UI:** provide access to and control over Airflow.
- **DAG processor:** reads and processes DAG definitions.
- **Triggerer:** supports asynchronous tasks.
- **Kubernetes task pods:** execute individual Airflow tasks.

### 7. Handle storage

- Determine whether the cluster supports dynamic persistent-volume
  provisioning.
- Configure persistence for PostgreSQL.
- Decide how DAG files and task logs will be stored.

Storage is likely to require additional configuration in this local cluster.

### 8. Install Airflow

Use `helm upgrade --install`, then examine the Kubernetes resources created by
the chart, including:

- Deployments
- StatefulSets
- Services
- Jobs
- Pods
- Secrets
- ConfigMaps

### 9. Access the Airflow UI

Initially use `kubectl port-forward`. Later, explore exposing Airflow using a
NodePort or Ingress.

### 10. Deploy our first DAG

- Add a simple DAG and run a task.
- Watch `KubernetesExecutor` create a temporary task pod.
- Inspect the pod logs and task result.

### 11. Improve toward production

Once the initial installation works, explore:

- Git-based DAG delivery
- External secret management
- External PostgreSQL
- Ingress and TLS
- Monitoring
- Backups
- Airflow and Helm chart upgrades

## Initial objective

The first objective is a small, working Airflow installation that we can study
and modify. It will not initially be a fully production-ready platform.

The bundled PostgreSQL deployment is suitable for learning. A production
deployment would normally use an external, managed database.

## References

- [Official Apache Airflow Helm chart](https://airflow.apache.org/docs/helm-chart/stable/index.html)
- [Airflow Helm chart production guide](https://airflow.apache.org/docs/helm-chart/stable/production-guide.html)
