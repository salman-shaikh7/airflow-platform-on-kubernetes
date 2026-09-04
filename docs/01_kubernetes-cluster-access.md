# Step 1: Configure Access to the Kubernetes Lab Cluster

## Cluster architecture

- Control plane: `192.168.122.131`
- Worker 1: `192.168.122.94`
- Worker 2: `192.168.122.38`
- Kubernetes API port: `6443`
- Local kubeconfig: `~/.kube/k8s-lab-config`

## Connect using kubectl

Tell kubectl which configuration file to use:

```bash
export KUBECONFIG="$HOME/.kube/k8s-lab-config"
```

To configure this automatically for every new Bash terminal:

```bash
grep -qxF 'export KUBECONFIG="$HOME/.kube/k8s-lab-config"' "$HOME/.bashrc" ||
echo 'export KUBECONFIG="$HOME/.kube/k8s-lab-config"' >> "$HOME/.bashrc"

source "$HOME/.bashrc"
```

Protect the kubeconfig because it contains cluster administrator credentials:

```bash
chmod 600 "$HOME/.kube/k8s-lab-config"
```

Confirm the active context:

```bash
kubectl config current-context
```

Test access:

```bash
kubectl cluster-info
kubectl get nodes
kubectl get pods --all-namespaces
```

If `KUBECONFIG` was added to `~/.bashrc`, new terminals load it automatically.
To reload it in the current terminal:

```bash
source "$HOME/.bashrc"
```

## Test the Kubernetes API connection

```bash
nc -vz 192.168.122.131 6443
```

This tests whether a TCP connection can be established to the Kubernetes API
server. It does not authenticate with Kubernetes.

## Connect using VS Code

1. Install the Microsoft Kubernetes extension.
2. Open the Kubernetes panel.
3. Configure its kubeconfig path as `/home/sal/.kube/k8s-lab-config`.
4. Refresh the Kubernetes panel.
5. Confirm that the three nodes and cluster namespaces are visible.

The VS Code extension and `kubectl` use the same kubeconfig file and
communicate with the same Kubernetes API server.

## Troubleshooting

```bash
kubectl config view --minify
kubectl get nodes
nc -vz 192.168.122.131 6443
```

If the virtual machines were restarted, confirm their IP addresses have not
changed.
