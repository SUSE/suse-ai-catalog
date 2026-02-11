# vLLM Runtime Module

Reusable Helm chart for vLLM model serving.

## Role in this Repo

This is a **module**. End users should normally deploy **profiles** under `fleet/profiles/`.

Profiles that use this module:

- `fleet/profiles/vllm-opt-125m`
- `fleet/profiles/vllm-llama3-8b`
- `fleet/profiles/vllm-mistral-7b`

## Creating a New vLLM Profile

1. Copy an existing profile directory under `fleet/profiles/`
2. Edit `values.yaml` (model, resources, scaling)
3. Keep `fleet.yaml` pointing chart to `../../vllm-runtime`
4. Point Rancher/Fleet GitRepo path at the new profile

## Common settings

- `model.name`
- `replicaCount`
- `resources.requests/limits`
- `vllm.extraArgs`
- `nodeSelector` / `tolerations`

## Optional Local Render Debug

```bash
helm template test-release . -n inference-system
```
