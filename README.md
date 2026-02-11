# SUSE AI Catalog

A catalog of Fleet-deployable AI/ML stacks with dependency management.

## Repository Structure

```
/
├── stacks.yaml          # Catalog of modules and stacks
├── fleet/               # Fleet bundles (one per module)
│   ├── vllm-runtime/
│   │   ├── fleet.yaml   # Fleet bundle config (Helm-based module)
│   │   ├── Chart.yaml
│   │   ├── values.yaml
│   │   ├── templates/
│   │   └── examples/
│   └── litellm-registry/
│       ├── fleet.yaml   # Fleet bundle config (Helm-based module)
│       ├── Chart.yaml
│       ├── values.yaml
│       ├── templates/
│       └── examples/
├── fleet/examples/       # Ready-to-apply Fleet GitRepo resources
├── schemas/
│   └── stacks.schema.json
└── scripts/
    └── validate_stacks.py
```

## Concepts

- **Module**: A deployable component (e.g., vLLM, LiteLLM, Kubeflow)
- **Stack**: A collection of modules with dependencies (e.g., Inference Core)
- **Fleet Bundle**: Kubernetes manifests packaged for Fleet deployment

## Quickstart

### 1. Validate the catalog

```bash
python3 scripts/validate_stacks.py stacks.yaml
```

### 2. Deploy with Fleet

Point Fleet at individual modules:

```bash
# Deploy vLLM runtime (default model)
kubectl apply -f - <<EOF
apiVersion: fleet.cattle.io/v1alpha1
kind: GitRepo
metadata:
  name: vllm-runtime
  namespace: fleet-default
spec:
  repo: <your-git-repo-url>
  paths:
  - fleet/vllm-runtime
  targetNamespace: inference-system
  helm:
    releaseName: vllm-opt-125m
EOF
```

**Deploy multiple models**: Create separate GitRepo resources with different values files:

```bash
# Deploy Llama 3 8B
kubectl apply -f - <<EOF
apiVersion: fleet.cattle.io/v1alpha1
kind: GitRepo
metadata:
  name: vllm-llama3
  namespace: fleet-default
spec:
  repo: <your-git-repo-url>
  paths:
  - fleet/vllm-runtime
  targetNamespace: inference-system
  helm:
    releaseName: vllm-llama3
    valuesFiles:
    - examples/values-llama3-8b.yaml
EOF
```

See [Deploying Multiple Models Guide](docs/deploying-multiple-models.md) for more examples.

Or deploy an entire stack by reading `stacks.yaml` and deploying modules in dependency order.

Example LiteLLM deployment with model routes:

```bash
kubectl apply -f fleet/examples/gitrepo-litellm-registry.yaml
```

### 3. Rancher Workflow (UI)

Most teams using Rancher create Fleet `GitRepo` resources from the Rancher UI:

1. Open Rancher and go to **Continuous Delivery**.
2. Select the Fleet workspace (usually `fleet-default`).
3. Click **Git Repos** -> **Create**.
4. Set:
   - **Repository URL**: your catalog repo URL
   - **Branch/Revision**: e.g. `main`
   - **Paths**: e.g. `fleet/vllm-runtime`
   - **Target Namespace**: `inference-system`
   - **Helm Release Name**: e.g. `vllm-opt-125m`
   - **Helm Values Files** (optional): e.g. `examples/values-llama3-8b.yaml`
5. Set cluster targeting (all clusters, label selectors, or specific clusters).
6. Save and watch bundle status in the Fleet dashboard.

Rancher then continuously reconciles the deployment from Git.

### 4. GitRepo-as-Code Workflow (`kubectl`)

You can also manage Fleet config declaratively by applying `GitRepo` resources:

```bash
kubectl apply -f fleet/examples/gitrepo-vllm-opt-125m.yaml
kubectl apply -f fleet/examples/gitrepo-vllm-llama3.yaml
kubectl apply -f fleet/examples/gitrepo-litellm-registry.yaml
```

This applies a `GitRepo` object into `fleet-default` (management cluster), and Fleet deploys to matching target clusters.

### 5. Test the deployment

```bash
# Port-forward default vLLM release
kubectl port-forward -n inference-system svc/vllm-opt-125m-vllm-runtime 8000:8000

# Test vLLM
curl http://localhost:8000/v1/models

# Port-forward LiteLLM
kubectl port-forward -n inference-system svc/litellm-registry 4000:4000

# Test LiteLLM (proxies to vLLM)
curl http://localhost:4000/v1/models
```

## Available Stacks

### inference-core

**Description**: Baseline model gateway and serving runtime for LLM inference.

**Modules**:
- `vllm-runtime` - GPU optimized LLM runtime (Helm chart, templatable)
- `litellm-registry` - Model registry and proxy

**Requirements**:
- NVIDIA GPU nodes with GPU operator installed
- Node labels: `nvidia.com/gpu.present=true`
- At least 1 GPU available per vLLM replica

**Deploy order** (respecting dependencies):
1. vllm-runtime
2. litellm-registry (depends on vllm-runtime)

**Key Features**:
- Deploy multiple vLLM instances with different models
- Configurable via Helm values (model, replicas, resources)
- See [Deploying Multiple Models Guide](docs/deploying-multiple-models.md)

## Deploying Multiple Models

This repo is Fleet-first. To run multiple models, create multiple Fleet `GitRepo` resources that point to `fleet/vllm-runtime` and use different `helm.releaseName` + `helm.valuesFiles`.

Example pattern:

```yaml
apiVersion: fleet.cattle.io/v1alpha1
kind: GitRepo
metadata:
  name: vllm-mistral
  namespace: fleet-default
spec:
  repo: <your-git-repo-url>
  paths:
  - fleet/vllm-runtime
  targetNamespace: inference-system
  helm:
    releaseName: vllm-mistral
    valuesFiles:
    - examples/values-mistral-7b.yaml
```

Each Fleet release gets its own service (for example `vllm-llama3-vllm-runtime` and `vllm-mistral-vllm-runtime`).

## CI/CD Strategy

See `.github/workflows/` for:
- **PR validation**: Lint stacks.yaml, validate modules, deploy affected stacks
- **Nightly tests**: Full stack matrix on fresh EKS clusters

## Adding a New Module

1. Create a new directory under `fleet/`:
   ```bash
   mkdir -p fleet/my-module
   ```

2. Add Kubernetes manifests and `fleet.yaml`:
   ```yaml
   # fleet/my-module/fleet.yaml
   defaultNamespace: my-namespace
   ```

3. Register the module in `stacks.yaml`:
   ```yaml
   modules:
     my-module:
       displayName: My Module
       description: What it does
       deploy:
         type: yaml
         path: fleet/my-module
       targetNamespace: my-namespace
   ```

4. Validate:
   ```bash
   python3 scripts/validate_stacks.py stacks.yaml
   ```

## Adding a New Stack

Edit `stacks.yaml` and add to the `stacks:` section:

```yaml
stacks:
  my-stack:
    displayName: My Stack
    description: Stack purpose
    category: Inference
    maintainers:
      - team@example.com
    modules:
      - id: module-one
      - id: module-two
        dependsOn:
          - module-one
```

## Troubleshooting

### Fleet Deployment Issues

**Error: "Namespace exists and cannot be imported"**

This happens if the namespace was created manually before Fleet tried to manage it. 

**Solution**: Delete the namespace or ensure the `defaultNamespace` in `fleet.yaml` handles namespace creation. Our bundles let Fleet manage the namespace automatically via `defaultNamespace`.

**Error: "missing key app.kubernetes.io/managed-by: must be set to Helm"**

Fleet is trying to manage resources as a Helm release. Ensure you don't have standalone `namespace.yaml` files that conflict with Fleet's namespace management.

### GPU Issues

**Error: "Failed to infer device type" or "No CUDA runtime is found"**

vLLM can't detect GPUs. This usually means:
1. GPU resources aren't requested in the deployment
2. Pod isn't scheduled on GPU nodes
3. NVIDIA GPU operator isn't installed or running

**Solution**:
```bash
# Check GPU operator is running
kubectl get pods -n gpu-operator-resources

# Verify GPU nodes are labeled
kubectl get nodes -l nvidia.com/gpu.present=true

# Check if pod has GPU allocated
kubectl describe pod -n inference-system -l app=vllm-runtime | grep nvidia.com/gpu
```

The vLLM module requests GPU resources by default in `fleet/vllm-runtime/values.yaml`. If your GPU nodes use different labels or taints, adjust `nodeSelector` and `tolerations` in values files.

## License

Apache 2.0
