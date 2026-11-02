---
name: rstack-mcp
description: Qualify a shared MCP service across multiple clients, including scoped state, cancellation, client adoption, idle shutdown and reconnect.
---

# rstack-mcp

Read [shared MCP](../../docs/shared-mcp.md) when sharing a service or replacing duplicate per-client instances. Bind the actual server, supported transport and client sessions before changing ownership.

Reuse the existing MCP implementation owner. Separate saved configuration, discovery, actual client adoption and sustained runtime behavior. Exercise only advertised capabilities and authorized effects.

Return a client-scoped lifecycle matrix and explicit gaps. One client's close or cancellation must not silently end another client's work. This skill does not install a server, launch a replacement service, create credentials or broaden permissions.
