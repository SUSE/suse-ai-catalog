#!/usr/bin/env python3
import argparse
import sys
from pathlib import Path

try:
    import yaml
except ImportError:  # pragma: no cover
    print("Missing dependency: PyYAML. Install with `pip install -r requirements.txt`.", file=sys.stderr)
    sys.exit(2)


def load_yaml(path: Path):
    with path.open("r", encoding="utf-8") as handle:
        return yaml.safe_load(handle)


def load_schema(path: Path):
    try:
        import json
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception as exc:
        raise RuntimeError(f"Failed to load schema: {path}") from exc


def validate_schema(data, schema_path: Path):
    try:
        from jsonschema import Draft202012Validator
    except ImportError:
        print("Warning: jsonschema not installed; skipping schema validation.", file=sys.stderr)
        return []

    schema = load_schema(schema_path)
    validator = Draft202012Validator(schema)
    errors = sorted(validator.iter_errors(data), key=lambda e: e.path)
    return errors


def validate_stack_dependencies(data):
    errors = []
    modules = data.get("modules") or {}
    stacks = data.get("stacks") or {}

    module_ids = set(modules.keys())
    for stack_id, stack in stacks.items():
        stack_modules = stack.get("modules") or []
        all_ids = [entry.get("id") for entry in stack_modules]
        all_ids_set = {mid for mid in all_ids if mid}
        seen_ids = set()

        for entry in stack_modules:
            module_id = entry.get("id")
            if not module_id:
                errors.append(f"stack '{stack_id}': module entry missing 'id'")
                continue
            if module_id in seen_ids:
                errors.append(f"stack '{stack_id}': duplicate module id '{module_id}'")
            seen_ids.add(module_id)

            if module_id not in module_ids:
                errors.append(f"stack '{stack_id}': unknown module id '{module_id}'")

            for dep in entry.get("dependsOn") or []:
                if dep not in module_ids:
                    errors.append(
                        f"stack '{stack_id}': module '{module_id}' depends on unknown module '{dep}'"
                    )
                if dep not in all_ids_set:
                    errors.append(
                        f"stack '{stack_id}': module '{module_id}' depends on '{dep}' not listed in stack"
                    )

        graph = {mid: [] for mid in all_ids_set}
        for entry in stack_modules:
            mid = entry.get("id")
            if mid not in graph:
                continue
            graph[mid] = list(entry.get("dependsOn") or [])

        visiting = set()
        visited = set()

        def dfs(node):
            if node in visited:
                return
            if node in visiting:
                errors.append(f"stack '{stack_id}': cyclic dependency detected at '{node}'")
                return
            visiting.add(node)
            for dep in graph.get(node, []):
                if dep in graph:
                    dfs(dep)
            visiting.remove(node)
            visited.add(node)

        for node in graph:
            dfs(node)

    return errors


def main():
    parser = argparse.ArgumentParser(description="Validate stacks.yaml schema and dependencies.")
    parser.add_argument(
        "stacks_file",
        nargs="?",
        default="stacks/stacks.yaml",
        help="Path to stacks.yaml (default: stacks/stacks.yaml)",
    )
    parser.add_argument(
        "--schema",
        default="schemas/stacks.schema.json",
        help="Path to JSON Schema (default: schemas/stacks.schema.json)",
    )
    args = parser.parse_args()

    stacks_path = Path(args.stacks_file)
    schema_path = Path(args.schema)
    if not stacks_path.exists():
        print(f"Stacks file not found: {stacks_path}", file=sys.stderr)
        return 2

    data = load_yaml(stacks_path) or {}

    schema_errors = validate_schema(data, schema_path)
    if schema_errors:
        print("Schema validation failed:", file=sys.stderr)
        for err in schema_errors:
            loc = "/".join(str(p) for p in err.path) or "<root>"
            print(f"  - {loc}: {err.message}", file=sys.stderr)

    dep_errors = validate_stack_dependencies(data)
    if dep_errors:
        print("Dependency validation failed:", file=sys.stderr)
        for err in dep_errors:
            print(f"  - {err}", file=sys.stderr)

    if schema_errors or dep_errors:
        return 1

    print("Validation OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
