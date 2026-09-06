# Technical Debt

Items intentionally deferred while building the lab platform.

## TD-001: Kubelet serving certificates lack IP SANs

**Status:** Open  
**Scope:** All three Kubernetes nodes

### Problem

Metrics Server connects to each kubelet over HTTPS using its internal IP and
port `10250`. The kubelet serving certificates do not contain the node IPs as
Subject Alternative Names (SANs), so TLS identity verification fails.

Observed error:

```text
x509: cannot validate certificate because it doesn't contain any IP SANs
```

### Impact

Components that directly connect to the kubelet API cannot securely verify the
kubelet's identity. Existing workloads and normal Kubernetes API operations are
not affected.

### Temporary lab workaround

Metrics Server uses `--kubelet-insecure-tls`. Traffic remains encrypted, but
the kubelet certificate's identity is not verified.

### Proper future fix

Configure kubelet serving-certificate bootstrap and rotation, review and
approve legitimate kubelet-serving CSRs, and ensure certificates are signed by
the cluster CA with the correct node DNS names and IP SANs. Then remove
`--kubelet-insecure-tls` and confirm Metrics Server can scrape every node.

### Completion checks

```bash
kubectl get csr
kubectl logs -n kube-system deployment/metrics-server
kubectl top nodes
```

This item is complete when metrics work without `--kubelet-insecure-tls` and
the Metrics Server logs contain no kubelet certificate-verification errors.
