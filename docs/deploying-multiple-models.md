# Deploying Multiple vLLM Models with Fleet Profiles

This repo uses a **module + profile** pattern:

- Modules: reusable charts (`fleet/vllm-runtime`, `fleet/litellm-registry`)
- Profiles: deployable Rancher/Fleet paths (`fleet/profiles/...`)

## Recommended Workflow

1. Deploy one vLLM profile per model backend
2. Deploy one LiteLLM profile that maps model aliases to those backends
3. Update profile values and let Fleet reconcile

## Deploy via Rancher UI

Create a Git Repo in Rancher Fleet and set path to each profile:

- `fleet/profiles/vllm-llama3-8b`
- `fleet/profiles/vllm-mistral-7b`
- `fleet/profiles/litellm-llama3-mistral`

No manual `valuesFiles` entry is needed in the UI.

## Deploy via GitRepo YAML

```bash
kubectl apply -f fleet/examples/gitrepo-vllm-llama3.yaml
kubectl apply -f fleet/examples/gitrepo-vllm-mistral.yaml
kubectl apply -f fleet/examples/gitrepo-litellm-registry.yaml
```

## Profile Values You Will Most Often Edit

### vLLM profile values (`fleet/profiles/vllm-*/values.yaml`)

- `model.name`
- `replicaCount`
- `resources`
- `vllm.extraArgs`

### LiteLLM profile values (`fleet/profiles/litellm-llama3-mistral/values.yaml`)

- `litellm.modelList[*].modelName`
- `litellm.modelList[*].apiBase`
- `litellm.existingSecretName` (production)

## Example LiteLLM model map

```yaml
litellm:
  modelList:
    - modelName: llama3-8b
      providerModel: openai/meta-llama/Meta-Llama-3-8B-Instruct
      apiBase: http://vllm-llama3-vllm-runtime.inference-system.svc.cluster.local:8000/v1
      apiKey: "dummy"

    - modelName: mistral-7b
      providerModel: openai/mistralai/Mistral-7B-Instruct-v0.3
      apiBase: http://vllm-mistral-vllm-runtime.inference-system.svc.cluster.local:8000/v1
      apiKey: "dummy"
```

## Production Hardening

- Create a real Secret and set `litellm.existingSecretName`
- Pin image tags to immutable versions
- Use separate profiles for dev/stage/prod when needed
