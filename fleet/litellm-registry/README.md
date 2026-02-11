# LiteLLM Registry Module

Reusable Helm chart for LiteLLM proxy and model alias routing.

## Role in this Repo

This is a **module**. End users should normally deploy profile bundles in `fleet/profiles/`.

Profile using this module:

- `fleet/profiles/litellm-llama3-mistral`

## Creating a New LiteLLM Profile

1. Copy an existing profile under `fleet/profiles/`
2. Update `litellm.modelList` aliases and `apiBase` routes
3. Set production secret reference:
   - `litellm.existingSecretName`
   - `litellm.existingSecretKey`
4. Point Rancher/Fleet GitRepo path at the new profile

## Security Best Practice

Use an externally managed Secret in production:

```bash
kubectl create secret generic litellm-master-key \
  -n inference-system \
  --from-literal=master-key='replace-with-strong-key'
```

Then in profile values:

```yaml
litellm:
  existingSecretName: litellm-master-key
  existingSecretKey: master-key
```

## Optional Local Render Debug

```bash
helm template test-litellm . -n inference-system
```
