# Step 9: Expose Airflow with Gateway API

## Outcome

Airflow is available from the laptop at:

```text
http://airflow.local
```

It no longer requires a temporary `kubectl port-forward` process.

```text
airflow.local → 192.168.122.200 → MetalLB → Envoy proxy
              → HTTPRoute → Airflow Service → Airflow API-server pod
```

## Architecture decision

Gateway API with Envoy Gateway was selected instead of starting a new Ingress
NGINX installation. Ingress NGINX was retired in March 2026, while Gateway API
is the modern Kubernetes routing model. A deeper comparison is tracked as
learning debt in [Technical Debt](08_technical-debt.md).

References:

- [Ingress NGINX retirement](https://kubernetes.io/blog/2025/11/11/ingress-nginx-retirement/)
- [Envoy Gateway Helm installation](https://gateway.envoyproxy.io/v1.9/install/install-helm/)

## 1. Install Envoy Gateway

Confirm that Gateway API CRDs are not already managed by another installation:

```bash
kubectl get crd gatewayclasses.gateway.networking.k8s.io gateways.gateway.networking.k8s.io httproutes.gateway.networking.k8s.io
```

Inspect the pinned chart:

```bash
helm show chart oci://docker.io/envoyproxy/gateway-helm --version v1.9.1
```

Install the CRDs and Envoy Gateway control plane:

```bash
helm install envoy-gateway oci://docker.io/envoyproxy/gateway-helm --version v1.9.1 --namespace envoy-gateway-system --create-namespace
```

Verify the controller:

```bash
kubectl wait --timeout=5m -n envoy-gateway-system deployment/envoy-gateway --for=condition=Available
```

```bash
kubectl get all -n envoy-gateway-system
```

The controller manages configuration. It does not carry application traffic.
Envoy data-plane pods are created after a `Gateway` is defined.

## 2. Create the GatewayClass

`kubernetes/networking/envoy-gateway-class.yaml` creates the cluster-scoped
`envoy-gateway` class. Its controller identifier connects future Gateways to
the Envoy Gateway controller:

```text
gateway.envoyproxy.io/gatewayclass-controller
```

```bash
kubectl apply -f kubernetes/networking/envoy-gateway-class.yaml
```

```bash
kubectl get gatewayclass
```

Expected condition: `ACCEPTED=True`.

## 3. Create the shared Gateway

`kubernetes/networking/platform-gateway.yaml` creates:

- The `platform-gateway` namespace.
- A Gateway using the `envoy-gateway` class.
- An HTTP listener on port `80`.
- Permission for routes in application namespaces to attach.

```bash
kubectl apply -f kubernetes/networking/platform-gateway.yaml
```

```bash
kubectl wait --for=condition=Programmed gateway/platform-gateway -n platform-gateway --timeout=5m
```

Envoy Gateway created an Envoy proxy Deployment and `LoadBalancer` Service.
MetalLB assigned the first available pool address:

```text
ADDRESS:     192.168.122.200
PROGRAMMED:  True
```

```bash
kubectl get services -A --field-selector=spec.type=LoadBalancer
```

## 4. Route Airflow traffic

`kubernetes/networking/airflow-http-route.yaml` attaches to the Gateway's
`http` listener and defines:

```text
Host airflow.local, path / → airflow/airflow-api-server:8080
```

```bash
kubectl apply -f kubernetes/networking/airflow-http-route.yaml
```

```bash
kubectl describe httproute airflow -n airflow
```

Successful route conditions:

```text
Accepted=True
ResolvedRefs=True
```

`Accepted` confirms attachment to the Gateway. `ResolvedRefs` confirms that
the Airflow backend Service and port were found.

## 5. Test routing

Test with the required hostname before changing local name resolution:

```bash
curl -sS -o /dev/null -w 'HTTP %{http_code}\n' -H 'Host: airflow.local' http://192.168.122.200
```

A request using `curl -I` returned `405 Method Not Allowed` because that option
sends `HEAD`, while the Airflow endpoint allows `GET`. The `server: uvicorn`
header still confirmed that the request reached Airflow.

## 6. Configure the laptop hostname

Add a local hostname mapping:

```bash
echo '192.168.122.200 airflow.local' | sudo tee -a /etc/hosts
```

Verify:

```bash
getent hosts airflow.local
```

Open [http://airflow.local](http://airflow.local). This mapping exists only on
this laptop; it is not public DNS.

## Current limitations

- Traffic currently uses HTTP rather than HTTPS.
- The Gateway permits routes from every namespace.
- The data plane has not yet been configured for high availability.
- `/etc/hosts` provides laptop-local name resolution rather than managed DNS.

These are future platform-hardening tasks, not blockers for the lab.
