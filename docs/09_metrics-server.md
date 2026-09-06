# Metrics Server

Metrics Server provides recent CPU and memory usage through the Kubernetes
Metrics API. It enables `kubectl top` and supplies resource metrics used by
features such as the Horizontal Pod Autoscaler.

## How it works

```text
Node kubelets
    ↓
Metrics Server pod
    ↓
metrics.k8s.io API
    ↓
kubectl top and autoscaling
```

Metrics Server runs as a single Deployment in the `kube-system` namespace. Its
internal Service gives the Kubernetes API aggregation layer a stable endpoint.

## 1. Download the manifest

```bash
mkdir -p kubernetes/monitoring
curl -fsSL \
  https://github.com/kubernetes-sigs/metrics-server/releases/latest/download/components.yaml \
  -o kubernetes/monitoring/metrics-server.yaml
```

## 2. Validate before installation

```bash
kubectl apply --dry-run=client \
  -f kubernetes/monitoring/metrics-server.yaml
```

The manifest creates the Deployment, Service, APIService, ServiceAccount, and
required RBAC resources.

## 3. Install Metrics Server

```bash
kubectl apply -f kubernetes/monitoring/metrics-server.yaml
```

Check its resources:

```bash
kubectl get deployment,pod,service -n kube-system \
  -l k8s-app=metrics-server
```

## 4. Lab TLS configuration

Metrics Server initially failed to scrape the kubelets because their serving
certificates do not contain the node IP addresses as SANs:

```text
x509: cannot validate certificate because it doesn't contain any IP SANs
```

For this isolated lab, the following argument was added to the Metrics Server
container's `args` list:

```yaml
- --kubelet-insecure-tls
```

This keeps traffic encrypted but disables kubelet identity verification. It is
a temporary lab workaround; the proper certificate fix is tracked in
[Technical Debt](08_technical-debt.md).

Apply the modified manifest and wait for the rollout:

```bash
kubectl apply -f kubernetes/monitoring/metrics-server.yaml
kubectl rollout status deployment/metrics-server -n kube-system
```

## 5. Verify live metrics

```bash
kubectl top nodes
kubectl top pods --all-namespaces
kubectl top pods --all-namespaces --containers
```

Useful sorted views:

```bash
kubectl top pods --all-namespaces --sort-by=memory
kubectl top pods --all-namespaces --sort-by=cpu
```

Metrics can take approximately 15–60 seconds to appear after Metrics Server
starts. Metrics Server supplies recent CPU and memory values only; it does not
provide historical dashboards, application logs, alerts, or disk metrics.

## Result

- Metrics Server Deployment is ready.
- The `metrics.k8s.io` API is available.
- Live node, pod, and container CPU and memory usage is accessible with
  `kubectl top`.
