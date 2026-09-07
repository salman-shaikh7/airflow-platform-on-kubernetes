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

## TD-002: Deepen Kubernetes ingress and Gateway API knowledge

**Status:** Open  
**Type:** Learning debt

### Topics to revisit

- How the legacy Kubernetes `Ingress` API and an Ingress controller work.
- The difference between NGINX, Ingress NGINX, and other controllers.
- Why Ingress NGINX was retired and how existing installations migrate.
- How Gateway API improves ownership, routing, extensibility, and portability.
- The roles of `GatewayClass`, `Gateway`, and `HTTPRoute`.
- How Envoy Gateway manages Envoy proxy data-plane pods.
- TLS termination, certificates, DNS, security policies, and multiple routes.

### Current decision

Use Gateway API with Envoy Gateway for the lab's permanent HTTP entry point.
Return to the topics above for a detailed comparison after the initial route to
Airflow is working.

## TD-003: Secure the Airflow Gateway with HTTPS

**Status:** Open
**Type:** Platform hardening

### Current state

Airflow is available at `http://airflow.local` through an unencrypted HTTP
Gateway listener. This is acceptable only for the isolated local lab.

### Future work

- Add a trusted development certificate for `airflow.local` using `mkcert`.
- Store the certificate and private key in a Kubernetes TLS Secret without
  committing private key material to Git.
- Add an HTTPS listener on port `443` and redirect HTTP to HTTPS.
- Study the production approach using real DNS, cert-manager, and an ACME or
  organizational certificate authority with automatic renewal.

This item is complete when the browser trusts `https://airflow.local`, HTTP is
redirected to HTTPS, and certificate renewal is documented.
