# Deploying Multiple vLLM Models with Fleet

Use one Fleet `GitRepo` per model deployment, all pointing to `fleet/vllm-runtime`, with different:

- `spec.helm.releaseName`
- `spec.helm.values`

Then deploy `fleet/litellm-registry` with `litellm.modelList` entries that route aliases to each vLLM service.

## Apply Example GitRepos

```bash
kubectl apply -f fleet/examples/gitrepo-vllm-llama3.yaml
kubectl apply -f fleet/examples/gitrepo-vllm-mistral.yaml
kubectl apply -f fleet/examples/gitrepo-litellm-registry.yaml
```

## Rancher UI

1. Create GitRepo with path `fleet/vllm-runtime`
2. Edit YAML to set `spec.helm.releaseName` and `spec.helm.values`
3. Repeat per model
4. Create LiteLLM GitRepo at `fleet/litellm-registry` with model map values

## Example LiteLLM Routing Values

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

## Production Notes

- Use external secret for LiteLLM master key (`existingSecretName`)
- Pin image tags
- Keep one GitRepo per model for isolated lifecycle/scaling
