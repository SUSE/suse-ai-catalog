# SUSE AI Catalog

A Fleet-first catalog of reusable AI modules and ready-to-deploy profiles.

## Design Goals

- Keep deploy logic modular and reusable
- Make Rancher UI workflow simple (choose a path, deploy)
- Avoid requiring `valuesFiles` input in Rancher UI forms

## Repository Layout

```
/
├── stacks.yaml
├── fleet/
│   ├── vllm-runtime/                  # Reusable Helm module (chart)
│   ├── litellm-registry/              # Reusable Helm module (chart)
│   ├── profiles/                      # UI-friendly deploy bundles
│   │   ├── vllm-opt-125m/
│   │   ├── vllm-llama3-8b/
│   │   ├── vllm-mistral-7b/
│   │   └── litellm-llama3-mistral/
│   └── examples/                      # Ready-to-apply GitRepo CRs
├── docs/
└── scripts/
```

## Concepts

- **Module**: Reusable implementation (`fleet/vllm-runtime`, `fleet/litellm-registry`)
- **Profile**: Deployable Fleet bundle with fixed release settings + values (`fleet/profiles/...`)
- **GitRepo**: Fleet CR that points to a profile path in this repo

## Why Profiles (Fleet Best Practice for Rancher UI)

Rancher UI often does not expose `valuesFiles` cleanly when creating a `GitRepo`.
Profiles solve this by bundling `fleet.yaml` + `values.yaml` together in a single path.

Users only choose:
- repo URL
- branch
- path (for example `fleet/profiles/vllm-llama3-8b`)

## Quick Start

### 1) Validate catalog metadata

```bash
python3 scripts/validate_stacks.py stacks.yaml
```

### 2) Deploy with Rancher UI

1. Rancher -> **Continuous Delivery**
2. Workspace: `fleet-default`
3. **Git Repos** -> **Create**
4. Set:
   - Repo URL: your fork/repo
   - Branch: `main`
   - Path: one of:
     - `fleet/profiles/vllm-opt-125m`
     - `fleet/profiles/vllm-llama3-8b`
     - `fleet/profiles/vllm-mistral-7b`
     - `fleet/profiles/litellm-llama3-mistral`
5. Save and watch bundle status

### 3) Deploy with GitRepo YAML (`kubectl`)

```bash
kubectl apply -f fleet/examples/gitrepo-vllm-opt-125m.yaml
kubectl apply -f fleet/examples/gitrepo-vllm-llama3.yaml
kubectl apply -f fleet/examples/gitrepo-vllm-mistral.yaml
kubectl apply -f fleet/examples/gitrepo-litellm-registry.yaml
```

## Multi-Model Pattern

Recommended rollout order:

1. Deploy one vLLM profile per model backend
   - `vllm-llama3-8b`
   - `vllm-mistral-7b`
2. Deploy LiteLLM profile that proxies aliases to those services
   - `litellm-llama3-mistral`

LiteLLM aliases are defined in:
- `fleet/profiles/litellm-llama3-mistral/values.yaml`

## Service Names

Profile release names produce stable service names:

- `vllm-llama3-vllm-runtime.inference-system.svc.cluster.local:8000`
- `vllm-mistral-vllm-runtime.inference-system.svc.cluster.local:8000`
- `litellm-registry-litellm-registry.inference-system.svc.cluster.local:4000`

## Security Notes

- LiteLLM master key is sourced from a Kubernetes Secret in chart templates
- Default values are dev-friendly; use existing Secret in production
- Pin image tags for production immutability

## Troubleshooting

### Namespace ownership error

If namespace was created manually before Fleet, Fleet/Helm ownership can conflict.
Use Fleet-managed namespace creation from bundle settings or recreate the namespace.

### vLLM cannot detect GPU

Check:

```bash
kubectl get pods -n gpu-operator-resources
kubectl get nodes -l nvidia.com/gpu.present=true
kubectl describe pod -n inference-system -l app=vllm-runtime | grep nvidia.com/gpu
```

Adjust `nodeSelector`/`tolerations` in profile values if your cluster labels differ.

## More Docs

- `docs/deploying-multiple-models.md`
- `fleet/vllm-runtime/README.md`
- `fleet/litellm-registry/README.md`
