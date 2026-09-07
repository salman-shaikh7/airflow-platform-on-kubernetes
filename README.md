# Airflow Platform

A hands-on learning project for deploying and operating Apache Airflow on a
local multi-node Kubernetes cluster.

## Initial goals

- Learn Kubernetes through practical exercises.
- Deploy Airflow to the cluster.
- Understand the main Airflow and Kubernetes components.
- Document the setup and decisions as the project develops.

## Documentation

- [Initial Airflow deployment plan](docs/00_plan_v1.md)
- [Step 1: Configure access to the Kubernetes cluster](docs/01_kubernetes-cluster-access.md)
- [Step 2: Inspect the Kubernetes cluster](docs/02_cluster-inspection.md)
- [Step 3: Install Helm](docs/03_helm-installation.md)
- [Step 4: Align the kubectl client version](docs/04_kubectl-version-alignment.md)
- [Step 5: Configure and test persistent storage](docs/05_persistent-storage.md)
- [Step 6: Deploy and troubleshoot Airflow](docs/06_airflow-deployment-troubleshooting.md)
- [Operations quick reference](docs/07_operations-quick-reference.md)
- [Technical debt](docs/08_technical-debt.md)
- [Step 7: Install and configure Metrics Server](docs/09_metrics-server.md)
- [Step 8: Configure MetalLB](docs/10_metallb-load-balancer.md)
- [Step 9: Expose Airflow with Gateway API](docs/11_gateway-api-envoy.md)

## Platform architecture

```mermaid
flowchart TB
  user([User])

  subgraph laptop["Laptop / Host Machine"]
    browser["Browser<br/>http://airflow.local"]
    kubectl["kubectl and Helm"]
    hosts["/etc/hosts<br/>airflow.local → 192.168.122.200"]
  end

  subgraph libvirt["Libvirt Virtual Network — 192.168.122.0/24"]
    apiEndpoint["Kubernetes API<br/>192.168.122.131:6443"]
    lbAddress["MetalLB address<br/>192.168.122.200:80"]
  end

  subgraph cluster["Kubernetes Cluster"]
    direction TB

    subgraph nodes["Three Ubuntu VMs"]
      control["Control plane<br/>192.168.122.131"]
      worker1["Worker 1<br/>192.168.122.94"]
      worker2["Worker 2<br/>192.168.122.38"]
    end

    subgraph platform["Platform Services"]
      calico["Calico<br/>Pod networking"]
      metrics["Metrics Server<br/>CPU and memory metrics"]
      storage["Local Path Provisioner<br/>Dynamic local volumes"]
      metallb["MetalLB<br/>LoadBalancer IP allocation + L2 announcement"]
      envoyController["Envoy Gateway Controller<br/>Gateway API management"]
    end

    subgraph traffic["Application Traffic Path"]
      envoyService["Envoy LoadBalancer Service"]
      envoyProxy["Envoy Proxy"]
      gateway["Gateway<br/>HTTP :80"]
      route["HTTPRoute<br/>Host: airflow.local"]
      airflowService["airflow-api-server Service<br/>ClusterIP :8080"]
    end

    subgraph airflow["Airflow Namespace"]
      api["API Server + Web UI"]
      scheduler["Scheduler"]
      dagProcessor["DAG Processor"]
      triggerer["Triggerer"]
      statsd["StatsD"]
      postgres[("PostgreSQL<br/>Airflow metadata")]
      taskPods["Temporary task Pods<br/>KubernetesExecutor"]
      pvc["PersistentVolumeClaim<br/>8 GiB, local-path"]
      nodeDisk[("Worker-node disk")]
    end
  end

  user --> browser
  user --> kubectl
  browser -. resolves through .-> hosts
  hosts --> lbAddress
  kubectl --> apiEndpoint --> control

  metallb -. assigns and advertises .-> lbAddress
  lbAddress --> envoyService --> envoyProxy
  envoyController -. configures .-> gateway
  gateway --> envoyProxy
  envoyProxy --> route --> airflowService --> api

  api --> postgres
  scheduler --> postgres
  dagProcessor --> postgres
  triggerer --> postgres
  scheduler -. creates through Kubernetes API .-> taskPods
  taskPods --> api
  scheduler -. emits metrics .-> statsd

  postgres --> pvc --> storage --> nodeDisk
  calico -. connects pods and services .-> airflowService
  metrics -. reads node and pod usage .-> nodes

  classDef person fill:#172554,stroke:#60a5fa,color:#fff,stroke-width:2px;
  classDef access fill:#eff6ff,stroke:#3b82f6,color:#172554;
  classDef network fill:#ecfeff,stroke:#06b6d4,color:#164e63;
  classDef platformSvc fill:#f5f3ff,stroke:#8b5cf6,color:#3b0764;
  classDef airflowSvc fill:#fff7ed,stroke:#f97316,color:#7c2d12;
  classDef data fill:#ecfdf5,stroke:#10b981,color:#064e3b;

  class user person;
  class browser,kubectl,hosts access;
  class apiEndpoint,lbAddress,envoyService,envoyProxy,gateway,route,airflowService network;
  class control,worker1,worker2,calico,metrics,storage,metallb,envoyController platformSvc;
  class api,scheduler,dagProcessor,triggerer,statsd,taskPods airflowSvc;
  class postgres,pvc,nodeDisk data;
```

## Status

Airflow is running on the Kubernetes cluster with `KubernetesExecutor`,
persistent PostgreSQL storage, and stable local UI access through MetalLB and
Envoy Gateway at [http://airflow.local](http://airflow.local).
