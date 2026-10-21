# Domain model, level 1

The vocabulary of an architecture diagram, in the words a reader and an author both use.

| Term | Meaning | Avoid |
|---|---|---|
| **Source** | the `.drawio` file an author edits. Plain XML, diffable. | calling it "the diagram file", which hides that a second file exists |
| **Artifact** | the committed `.drawio.svg` a reader sees. It carries the source inside it. | calling it "the export", which implies the source is disposable |
| **House style** | the pinned palette, type scale, spacing and edge rules. | calling it "the theme", which suggests a styling option rather than a contract |
| **Cluster** | a container shape that groups shapes by tier or by concern. | calling it "a box", which says nothing about what it is for |
| **Service shape** | a shape standing for one service or process. | "node", which is what a diagram library calls it |
| **Datastore shape** | a cylinder shape standing for a database or ledger. | "table", which is not what it usually is |
| **Edge** | a connection between two shapes, with an optional label on it. | "arrow", which says nothing about what it means |
| **Drift** | a committed artifact that no longer matches its source. | "a stale file", which names the symptom rather than the failure |
| **Look** | the step where an author views the rendered artifact and corrects what reads badly. | "review", which a validator already does |
