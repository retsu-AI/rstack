# Diagram evidence with Pele

Use this reference when the requested artifact includes a diagram. Bind its editable source, rendered output and inspection to the same acceptance criteria and revision as the implementation. Follow [exact-subject verification](verification.md); a renderer result alone cannot establish correspondence with the system.

## Package and interface

The selected library is npm `pele`, maintained at [obsidianmd/pele](https://github.com/obsidianmd/pele), with documentation at [pele.run](https://pele.run). The [1.11.0 package metadata](https://raw.githubusercontent.com/obsidianmd/pele/1.11.0/package.json) identifies the package and `dist/pele.js` module entry. Use the project's pinned version and record it; this reference does not install or upgrade a renderer.

The full module exports synchronous `render(source, options)`. It returns an object containing `svg`, `width`, `height`, `type`, `mermaidType` and `links`. Read the installed version's types and [API documentation](https://pele.run/api) before choosing options or a smaller/lazy entrypoint. For an existing authorized setup, a minimal source example is:

```js
import { render } from 'pele';

const result = render('flowchart LR\n Plan --> Work --> Verify');
const svg = result.svg;
```

This example has not rendered an artifact for the current task. Preserve the actual render invocation, result and output when executing it.

Pele targets Mermaid syntax with its own layout and styling. External Mermaid plugins, arbitrary HTML labels and all Mermaid configuration options are not interchangeable. Check the exact syntax and diagram type against [compatibility](https://pele.run/compatibility), including the selected version. Record a parse/render error instead of silently changing the source or claiming full Mermaid compatibility.

## Review the artifact

Keep a compact evidence record with source and artifact paths/revisions, acceptance IDs, renderer version, options, fonts/theme, output dimensions, and render result or error. When embedded or exported, retain the actual viewport/page, scale and relevant export settings. Changing source, renderer, options or presentation stales affected visual acceptance.

| Check | Evidence required |
|---|---|
| Source and structure | Compare required components, edges, labels, states and transitions with the requirements and implementation; record omissions. |
| Render | Retain the actual SVG or export and parse/render result for the frozen source. |
| Visual inspection | Inspect the rendered pixels for clipping, overlap, unreadable text and misleading connections; name inspected views/pages, resolution and coverage denominator. |

Record these checks separately. Text inspection does not establish pixel coverage. An SVG file that exists but was never viewed remains visually unobserved. If the requested renderer is unavailable, name that dependency and preserve its acceptance criterion as open. Return corrections to the author, rerender changed artifacts, and have the independent verifier inspect the affected result before the manager accepts the integrated package.

The [formal architecture example](formal-architecture-example.md) supplies an editable flowchart and requirement-to-state/proof crosswalk. Its source existing is not a render or pixel-inspection result.
