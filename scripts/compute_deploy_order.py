#!/usr/bin/env python3
"""
Compute the deployment order for a stack based on module dependencies.

Usage:
    python scripts/compute_deploy_order.py stacks.yaml inference-core
"""

import sys
import yaml
from collections import defaultdict, deque


def topological_sort(modules_in_stack):
    """
    Perform topological sort on modules to determine deployment order.
    
    Args:
        modules_in_stack: List of dicts with 'id' and optional 'dependsOn'
    
    Returns:
        List of module IDs in deployment order
    """
    # Build adjacency list and in-degree map
    graph = defaultdict(list)
    in_degree = {mod['id']: 0 for mod in modules_in_stack}
    
    for mod in modules_in_stack:
        mod_id = mod['id']
        deps = mod.get('dependsOn', [])
        
        for dep in deps:
            graph[dep].append(mod_id)
            in_degree[mod_id] += 1
    
    # Kahn's algorithm
    queue = deque([mod for mod in in_degree if in_degree[mod] == 0])
    result = []
    
    while queue:
        current = queue.popleft()
        result.append(current)
        
        for neighbor in graph[current]:
            in_degree[neighbor] -= 1
            if in_degree[neighbor] == 0:
                queue.append(neighbor)
    
    if len(result) != len(modules_in_stack):
        raise ValueError("Dependency cycle detected in stack modules")
    
    return result


def main():
    if len(sys.argv) != 3:
        print("Usage: python scripts/compute_deploy_order.py stacks.yaml <stack-name>")
        sys.exit(1)
    
    stacks_file = sys.argv[1]
    stack_name = sys.argv[2]
    
    try:
        with open(stacks_file, 'r') as f:
            data = yaml.safe_load(f)
        
        if stack_name not in data.get('stacks', {}):
            print(f"Error: Stack '{stack_name}' not found in {stacks_file}")
            sys.exit(1)
        
        stack = data['stacks'][stack_name]
        modules_in_stack = stack.get('modules', [])
        
        if not modules_in_stack:
            print(f"Warning: Stack '{stack_name}' has no modules")
            sys.exit(0)
        
        deploy_order = topological_sort(modules_in_stack)
        
        print(f"Deployment order for stack '{stack_name}':")
        for i, mod_id in enumerate(deploy_order, 1):
            module_info = data['modules'].get(mod_id, {})
            display_name = module_info.get('displayName', mod_id)
            print(f"  {i}. {mod_id} ({display_name})")
        
        # Output as space-separated list for CI
        print("\n# For CI (space-separated):")
        print(" ".join(deploy_order))
        
    except FileNotFoundError:
        print(f"Error: File '{stacks_file}' not found")
        sys.exit(1)
    except yaml.YAMLError as e:
        print(f"Error parsing YAML: {e}")
        sys.exit(1)
    except ValueError as e:
        print(f"Error: {e}")
        sys.exit(1)


if __name__ == '__main__':
    main()
