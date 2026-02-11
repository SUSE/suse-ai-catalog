# SUSE AI Catalog

Fleet-first catalog of deployable AI modules.

## Recommended Fleet Pattern (Works in Rancher)

Use one `GitRepo` per deployment and point `paths` directly to module directories:

- `fleet/vllm-runtime`
- `fleet/litellm-registry`

Set model-specific config in `spec.helm.values` (inline YAML in GitRepo).

This avoids UI limitations around `valuesFiles` and avoids cross-path chart references.

## Quick Start

### 1) Validate catalog metadata

```bash
python3 scripts/validate_stacks.py stacks.yaml
```

### 2) Apply example GitRepo resources

```bash
kubectl apply -f fleet/examples/gitrepo-vllm-opt-125m.yaml
kubectl apply -f fleet/examples/gitrepo-vllm-llama3.yaml
kubectl apply -f fleet/examples/gitrepo-vllm-mistral.yaml
kubectl apply -f fleet/examples/gitrepo-litellm-registry.yaml
```

### 3) Rancher UI workflow

If using Rancher UI, create GitRepo and set:

- Repo URL
- Branch
- Path: `fleet/vllm-runtime` (or `fleet/litellm-registry`)

Then use **Edit YAML** to add `spec.helm.releaseName` and `spec.helm.values`.

## Multi-Model Deployment Model

- Deploy one vLLM GitRepo per model (`releaseName` differs)
- Deploy one LiteLLM GitRepo with `litellm.modelList` routes to those vLLM services

Example vLLM service names:

- `vllm-llama3-vllm-runtime.inference-system.svc.cluster.local:8000`
- `vllm-mistral-vllm-runtime.inference-system.svc.cluster.local:8000`

## Why Not Path-Based Profiles Referencing `../../chart`

Fleet can report `no resource found at path` when a selected path is not self-contained as a deployable bundle/chart.
Cross-directory chart references in profile-only paths are less reliable across environments.

Module-path GitRepos + inline values are the more robust Fleet pattern.

## Repository Layout

```
/
├── stacks.yaml
├── fleet/
│   ├── vllm-runtime/
│   ├── litellm-registry/
│   └── examples/
├── docs/
└── scripts/
```

## More Docs

- `docs/deploying-multiple-models.md`
- `fleet/vllm-runtime/README.md`
- `fleet/litellm-registry/README.md`
