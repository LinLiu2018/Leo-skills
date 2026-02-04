#!/usr/bin/env python
# -*- coding: utf-8 -*-
import sys
sys.path.insert(0, 'src')

try:
    from leo_orchestrator.registry import get_registry
    r = get_registry()
    print(f"Skills: {len(r.get('skills', []))}")
    print(f"Agents: {len(r.get('agents', []))}")
    print(f"Workflows: {len(r.get('workflows', []))}")
    print("MCP Server: OK")
except Exception as e:
    print(f"Error: {e}")
    sys.exit(1)
