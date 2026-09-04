# Step 4: Align the kubectl Client Version

Completion date: 2026-09-03

## Objective

Align the local `kubectl` client with the Kubernetes API server version.

The initial inspection found:

```text
Client Version: v1.36.3
Server Version: v1.34.11
```

This exceeded Kubernetes' supported `kubectl` version skew of one minor
version.

## Existing installation

The original client was a manually installed system binary:

```text
/usr/local/bin/kubectl
```

It was not managed by APT or Snap. The system binary was left unchanged
because replacing it required interactive `sudo` authentication.

## Download and checksum verification

The matching Linux AMD64 client and its checksum were downloaded from the
official Kubernetes release site:

```bash
curl -fLO https://dl.k8s.io/release/v1.34.11/bin/linux/amd64/kubectl
curl -fLO https://dl.k8s.io/release/v1.34.11/bin/linux/amd64/kubectl.sha256
echo "$(cat kubectl.sha256)  kubectl" | sha256sum --check
```

Checksum result:

```text
kubectl: OK
```

## User-local installation

The verified binary was installed without `sudo`:

```bash
install -d -m 0755 "$HOME/.local/bin"
install -m 0755 kubectl "$HOME/.local/bin/kubectl"
hash -r
```

The active path is:

```text
/home/sal/.local/bin/kubectl
```

`~/.local/bin` appears before `/usr/local/bin` in `PATH`, so normal `kubectl`
commands use the matching user-local client. The previous system-level client
remains available at `/usr/local/bin/kubectl`.

## Verification

Commands:

```bash
command -v kubectl
kubectl version
kubectl get nodes -o wide
```

Results:

```text
Client Version: v1.34.11
Kustomize Version: v5.7.1
Server Version: v1.34.11
```

All nodes remained ready:

| Node | Status | Kubernetes version |
|---|---|---|
| `k8s-control-plane` | Ready | `v1.34.11` |
| `k8s-worker-1` | Ready | `v1.34.11` |
| `k8s-worker-2` | Ready | `v1.34.11` |

Status: **Completed successfully**

## Reference

- [Install and set up kubectl on Linux](https://kubernetes.io/docs/tasks/tools/install-kubectl-linux/)
