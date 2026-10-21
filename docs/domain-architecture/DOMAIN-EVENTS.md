# Domain events

Events that cross a boundary in the workflow.

| Event | Produced by | Consumed by | What it carries |
|---|---|---|---|
| **Source authored** | the authoring step | the render script | a `.drawio` file on disk |
| **Artifact rendered** | the render script | the staleness gate, the commit | a `.drawio.svg` carrying the diagram XML |
| **Drift detected** | the staleness gate | the build | the cell, the attribute, and the two values that disagree |
