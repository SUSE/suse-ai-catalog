# vLLM Runtime Fleet Module

GPU-optimized LLM serving module deployed by Fleet.

## How This Module Is Used

This directory is a Fleet bundle that renders a Helm chart (`chart: .` in `fleet.yaml`).
Users should deploy it through Fleet `GitRepo` resources, not direct Helm CLI installs.

## Fleet Deployment

### Default model (from `values.yaml`)

```yaml
apiVersion: fleet.cattle.io/v1alpha1
kind: GitRepo
metadata:
  name: vllm-opt-125m
  namespace: fleet-default
spec:
  repo: <your-repo-url>
  paths:
    - fleet/vllm-runtime
  targetNamespace: inference-system
  helm:
    releaseName: vllm-opt-125m
```

### Specific model via values file

```yaml
apiVersion: fleet.cattle.io/v1alpha1
kind: GitRepo
metadata:
  name: vllm-llama3
  namespace: fleet-default
spec:
  repo: <your-repo-url>
  paths:
    - fleet/vllm-runtime
  targetNamespace: inference-system
  helm:
    releaseName: vllm-llama3
    valuesFiles:
      - examples/values-llama3-8b.yaml
```

## Rancher UI Workflow

If you use Rancher UI instead of `kubectl`:

1. Rancher -> **Continuous Delivery**.
2. Open workspace `fleet-default`.
3. Create a new **Git Repo**.
4. Set path to `fleet/vllm-runtime`.
5. Set Helm release name (for example `vllm-llama3`).
6. Optionally set Helm values file (for example `examples/values-llama3-8b.yaml`).
7. Save and monitor bundle rollout.

## Multiple Models Pattern

Run one Fleet `GitRepo` per model/release:

- `vllm-llama3`
- `vllm-mistral`
- `vllm-opt-125m`

Each release gets an independent Deployment and Service, so scale and upgrades are isolated per model.

## Configuration

Set model and scaling behavior through values files:

- `model.name`
- `model.maxModelLen`
- `replicaCount`
- `resources`
- `vllm.extraArgs`
- `nodeSelector` / `tolerations`

See `values.yaml` and `examples/`.

## Service Naming

Service name format is based on Helm release + chart name.

Examples:

- `vllm-llama3-vllm-runtime.inference-system.svc.cluster.local:8000`
- `vllm-mistral-vllm-runtime.inference-system.svc.cluster.local:8000`

Use these service URLs in LiteLLM `api_base` entries.

## Optional Local Debug (Not Primary Workflow)

If you need to inspect rendered manifests locally:

```bash
helm template test-release . -n inference-system
```

## Requirements

- NVIDIA GPU Operator installed
- GPU nodes schedulable for this workload
- Adequate memory/GPU per model profile
