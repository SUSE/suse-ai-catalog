# SUSE AI Catalog

A catalog of Fleet-deployable AI/ML stacks with dependency management.

## Repository Structure

```
/
├── stacks.yaml          # Catalog of modules and stacks
├── fleet/               # Fleet bundles (one per module)
│   ├── vllm-runtime/
│   │   ├── fleet.yaml   # Fleet bundle config
│   │   ├── namespace.yaml
│   │   ├── deployment.yaml
│   │   └── service.yaml
│   └── litellm-registry/
│       ├── fleet.yaml
│       ├── configmap.yaml
│       ├── deployment.yaml
│       └── service.yaml
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
# Deploy vLLM runtime
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
EOF
```

Or deploy an entire stack by reading `stacks.yaml` and deploying modules in dependency order.

### 3. Test the deployment

```bash
# Port-forward vLLM
kubectl port-forward -n inference-system svc/vllm-runtime 8000:8000

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
- `vllm-runtime` - GPU optimized LLM runtime
- `litellm-registry` - Model registry and proxy

**Deploy order** (respecting dependencies):
1. vllm-runtime
2. litellm-registry (depends on vllm-runtime)

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

## License

Apache 2.0
