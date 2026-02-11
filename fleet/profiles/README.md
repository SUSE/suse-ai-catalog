# Fleet Profiles

Profiles are path-based Fleet bundles intended for Rancher UI deployment.

Each profile contains:

- `fleet.yaml` (release + chart reference)
- `values.yaml` (profile-specific configuration)

## Available Profiles

- `vllm-opt-125m`
- `vllm-llama3-8b`
- `vllm-mistral-7b`
- `litellm-llama3-mistral`

## Rancher UI Use

When creating a Fleet Git Repo in Rancher, set path directly to one profile, for example:

- `fleet/profiles/vllm-llama3-8b`

This avoids requiring Helm values input in the UI.
