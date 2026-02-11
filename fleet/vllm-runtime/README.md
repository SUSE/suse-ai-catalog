# vLLM Runtime Module

Reusable Fleet/Helm module for vLLM serving.

## Deploy Pattern

Create one Fleet `GitRepo` per model, each pointing to this path:

- `fleet/vllm-runtime`

Set per-model settings in `spec.helm.values`:

- `model.name`
- `replicaCount`
- `resources`
- `vllm.extraArgs`

See examples in `fleet/examples/`.
