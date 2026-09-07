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

## TD-006: Make monitoring storage durable

**Status:** Open  
**Type:** Platform reliability

### Current state

Prometheus and Grafana were installed with persistence disabled to conserve
resources during initial lab work. Prometheus retains metrics for 24 hours on
the pod's temporary filesystem; Grafana dashboards and settings are also
stored temporarily. Their data disappears if the pods are recreated.

Airflow task logs are separate and are stored persistently in the MinIO PVC.

### Future work

- Give Prometheus a persistent volume and define an appropriate retention
  policy.
- Give Grafana a persistent volume or provision dashboards and data sources
  entirely from Git.
- Evaluate long-term metrics storage such as Thanos, Mimir, or a managed
  monitoring service.

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

## TD-004: Understand Airflow UI sessions and JWT authentication

**Status:** Open
**Type:** Learning debt

### Current understanding

After login, the Airflow UI stores a signed JWT in the browser's `_token`
cookie. The browser sends it with later requests, and the API server validates
it using the shared `airflow-jwt-secret`. Because replacement API-server pods
use the same secret, pod restarts do not normally invalidate existing sessions.

### Topics to revisit

- JWT claims, signatures, issuer, audience, and expiration.
- The UI token cookie and browser cookie security attributes.
- Default and customized session expiration times.
- Automatic token refresh and server-side token revocation.
- Logout behaviour and the `revoked_token` database table.
- JWT secret storage, rotation, and multiple API-server replicas.
- The difference between UI/API tokens and internal task execution tokens.
- How HTTPS protects authentication cookies in transit.

### Useful check

```bash
kubectl exec -n airflow deployment/airflow-api-server -c api-server -- airflow config get-value api_auth jwt_expiration_time
```

This item is complete when the login, validation, refresh, expiration,
revocation, and secret-rotation lifecycle has been tested and documented.

## TD-005: Airflow live-log lookup before remote logs

**Status:** Open  
**Type:** Learning / UX debt

### Current behavior

With `KubernetesExecutor`, Airflow tries to read logs from the temporary task
pod while a task is running. After the task finishes, the UI reads the durable
copy from MinIO (`s3://airflow-logs`). Setting
`apiServer.allowPodLogReading: false` blocks Kubernetes pod-log access, but does
not remove the UI's initial live-log lookup; it can therefore display a
harmless `403 Forbidden` message before showing the remote log.

### Upstream references

- [Airflow issue #21387](https://github.com/apache/airflow/issues/21387)
- [Airflow issue #45516](https://github.com/apache/airflow/issues/45516)
- [Airflow discussion #45624](https://github.com/apache/airflow/discussions/45624)

### Future work

Study Airflow's live-log selection path and determine whether a future Airflow
release adds a supported way to suppress the initial pod lookup. Keep remote
object storage as the authoritative source and avoid custom UI patches unless
there is a clear operational need.
