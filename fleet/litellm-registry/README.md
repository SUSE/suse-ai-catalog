# LiteLLM Registry Module

Reusable Fleet/Helm module for proxying model aliases to vLLM backends.

## Deploy Pattern

Create a Fleet `GitRepo` pointing to:

- `fleet/litellm-registry`

Set routes in `spec.helm.values.litellm.modelList`.

Use external secret in production:

- `litellm.existingSecretName`
- `litellm.existingSecretKey`

See examples in `fleet/examples/`.
