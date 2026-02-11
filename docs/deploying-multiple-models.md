# Deploying Multiple vLLM Instances with Fleet

Deploy one Fleet `GitRepo` per model. Each `GitRepo` points at `fleet/vllm-runtime` and uses a distinct `helm.releaseName` and optional `helm.valuesFiles`.

## Choose Your Control Plane Workflow

### Option A: Rancher UI (most common)

1. Rancher -> **Continuous Delivery**.
2. Open workspace `fleet-default`.
3. **Git Repos** -> **Create**.
4. Set repo URL, branch, path `fleet/vllm-runtime`, target namespace, and Helm settings.
5. Save and monitor bundle health in Fleet UI.

### Option B: GitRepo as YAML (`kubectl`)

Use the provided examples:

```bash
kubectl apply -f fleet/examples/gitrepo-vllm-opt-125m.yaml
kubectl apply -f fleet/examples/gitrepo-vllm-llama3.yaml
```

These `GitRepo` resources are applied to `fleet-default` on the Rancher management cluster.

## Recommended Pattern

- One release per model
- Model-specific values file per release
- Independent scaling and rollout per model

## Example: Three Models

```yaml
---
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

---
apiVersion: fleet.cattle.io/v1alpha1
kind: GitRepo
metadata:
  name: vllm-mistral
  namespace: fleet-default
spec:
  repo: <your-repo-url>
  paths:
    - fleet/vllm-runtime
  targetNamespace: inference-system
  helm:
    releaseName: vllm-mistral
    valuesFiles:
      - examples/values-mistral-7b.yaml

---
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

## Custom Model Values File

Create a values file in-repo (example: `fleet/vllm-runtime/examples/values-gemma-7b.yaml`):

```yaml
model:
  name: "google/gemma-7b"
  maxModelLen: 4096

replicaCount: 2

resources:
  requests:
    memory: "16Gi"
    nvidia.com/gpu: "1"
  limits:
    memory: "24Gi"
    nvidia.com/gpu: "1"

vllm:
  extraArgs:
    - "--dtype=float16"
```

Then reference it from a Fleet `GitRepo` using `helm.valuesFiles`.

## Integrating with LiteLLM

Point each LiteLLM model entry to a vLLM service by editing `fleet/litellm-registry/examples/values-llama3-mistral.yaml`:

```yaml
model_list:
  - model_name: llama3-8b
    litellm_params:
      model: openai/meta-llama/Meta-Llama-3-8B-Instruct
      api_base: http://vllm-llama3-vllm-runtime.inference-system.svc.cluster.local:8000/v1
      api_key: "dummy"

  - model_name: mistral-7b
    litellm_params:
      model: openai/mistralai/Mistral-7B-Instruct-v0.3
      api_base: http://vllm-mistral-vllm-runtime.inference-system.svc.cluster.local:8000/v1
      api_key: "dummy"
```

Then apply/update the LiteLLM Fleet release:

```bash
kubectl apply -f fleet/examples/gitrepo-litellm-registry.yaml
```

## Operations Checklist

- Use stable release names (`vllm-llama3`, `vllm-mistral`)
- Pin image tags in values
- Keep one values file per model profile
- Scale by editing values and letting Fleet reconcile
