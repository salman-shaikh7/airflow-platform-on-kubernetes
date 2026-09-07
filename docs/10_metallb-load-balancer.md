# Step 8: Configure MetalLB

## Outcome

MetalLB `v0.16.1` provides `LoadBalancer` Services with addresses from
`192.168.122.200–210`. An NGINX test confirmed that `192.168.122.200` was
reachable from the laptop, and the temporary test resources were removed.

## Why MetalLB is needed

Cloud providers normally allocate and route external addresses for Kubernetes
`LoadBalancer` Services. This local libvirt cluster has no cloud load-balancer
integration, so MetalLB provides that functionality inside the cluster.

```text
Laptop → virtual LoadBalancer IP → MetalLB speaker/node
       → Kubernetes Service → healthy pod
```

The controller assigns addresses. A speaker pod on each node can advertise an
assigned address to the local network. Kubernetes Service networking handles
traffic after it reaches a node.

## 1. Reserve addresses in the libvirt network

The network uses `192.168.122.0/24`. Its original DHCP range occupied
`.2–254`, leaving no address guaranteed to be safe for MetalLB.

Back up the network definition locally:

```bash
mkdir -p backups
```

```bash
virsh net-dumpxml default > backups/libvirt-default-network-before-metallb.xml
```

The `backups/` directory is ignored by Git because it contains machine-specific
configuration and MAC addresses.

Reduce the DHCP range:

```bash
virsh net-update default delete ip-dhcp-range "<range start='192.168.122.2' end='192.168.122.254'/>" --live --config
```

```bash
virsh net-update default add ip-dhcp-range "<range start='192.168.122.2' end='192.168.122.199'/>" --live --config
```

This reserves `.200–210` for MetalLB and leaves the existing VM addresses
inside the DHCP range.

## 2. Check the kube-proxy prerequisite

```bash
kubectl get configmap kube-proxy -n kube-system -o jsonpath='{.data.config\.conf}' | grep -E '^[[:space:]]*(mode|strictARP):'
```

Observed:

```text
strictARP: false
mode: ""
```

An empty mode uses the default Linux Service implementation, normally
`iptables`. The MetalLB `strictARP` adjustment is required for IPVS mode, so no
change was needed.

## 3. Install MetalLB

Download a pinned native-mode manifest suitable for Layer 2 operation:

```bash
mkdir -p kubernetes/networking && curl -fsSL https://raw.githubusercontent.com/metallb/metallb/v0.16.1/config/manifests/metallb-native.yaml -o kubernetes/networking/metallb-native.yaml
```

Validate and install:

```bash
kubectl apply --dry-run=client -f kubernetes/networking/metallb-native.yaml
```

```bash
kubectl apply -f kubernetes/networking/metallb-native.yaml
```

```bash
kubectl rollout status deployment/controller -n metallb-system
```

```bash
kubectl rollout status daemonset/speaker -n metallb-system
```

The result is one controller pod and one speaker pod on each of the three
nodes.

## 4. Configure the address pool

The file `kubernetes/networking/metallb-config.yaml` defines:

- `IPAddressPool`: addresses `.200–210` may be allocated.
- `L2Advertisement`: speakers may advertise addresses from that pool.

```bash
kubectl apply --dry-run=client -f kubernetes/networking/metallb-config.yaml
```

```bash
kubectl apply -f kubernetes/networking/metallb-config.yaml
```

```bash
kubectl get ipaddresspool,l2advertisement -n metallb-system
```

## 5. Test the complete path

`kubernetes/networking/metallb-test.yaml` created a temporary namespace, NGINX
Deployment, and `LoadBalancer` Service.

```bash
kubectl apply -f kubernetes/networking/metallb-test.yaml
```

```bash
kubectl rollout status deployment/nginx -n metallb-test
```

```bash
kubectl get service nginx -n metallb-test
```

MetalLB assigned `192.168.122.200`. Access from the laptop succeeded:

```bash
curl -I http://192.168.122.200
```

```text
HTTP/1.1 200 OK
Server: nginx
```

The laptop's neighbor table showed that worker 1's speaker advertised the
virtual address:

```bash
ip neigh show 192.168.122.200
```

## 6. Remove the test workload

```bash
kubectl delete namespace metallb-test
```

The test Service, Deployment, and pod were deleted, and `.200` returned to the
MetalLB pool. MetalLB itself and its address-pool configuration remain active
for the upcoming Ingress controller.
