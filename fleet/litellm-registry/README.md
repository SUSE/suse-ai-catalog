# LiteLLM Registry Fleet Module

Fleet-managed LiteLLM proxy that routes model aliases to one or more vLLM backends.

## Purpose

- Keep vLLM deployments modular (one release per model/backend).
- Configure proxy routes in LiteLLM with values files.
- Let users call one LiteLLM endpoint and choose model alias.

## Fleet Usage

Create a Fleet `GitRepo` that points to this module:

```yaml
apiVersion: fleet.cattle.io/v1alpha1
kind: GitRepo
metadata:
  name: litellm-registry
  namespace: fleet-default
spec:
  repo: <your-git-repo-url>
  branch: main
  paths:
    - fleet/litellm-registry
  targetNamespace: inference-system
  helm:
    releaseName: litellm-registry
    valuesFiles:
      - examples/values-llama3-mistral.yaml
```

## Routing Model Aliases

Routes are configured in `litellm.modelList`:

```yaml
litellm:
  modelList:
    - modelName: llama3-8b
      providerModel: openai/meta-llama/Meta-Llama-3-8B-Instruct
      apiBase: http://vllm-llama3-vllm-runtime.inference-system.svc.cluster.local:8000/v1
      apiKey: "dummy"
```

`modelName` is what clients send to LiteLLM in API requests.

## Secret Management (Best Practice)

By default, the chart creates a Secret for `LITELLM_MASTER_KEY` from
`litellm.masterKey` so the module works out-of-the-box.

For production, use a pre-created Secret instead:

```yaml
litellm:
  existingSecretName: litellm-master-key
  existingSecretKey: master-key
```

And create the Secret separately (example):

```bash
kubectl create secret generic litellm-master-key \
  -n inference-system \
  --from-literal=master-key='replace-with-strong-key'
```

## Optional Local Debug

```bash
helm template test-litellm . -n inference-system
```
