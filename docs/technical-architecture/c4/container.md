# Containers

| Container | What it runs | Runtime |
|---|---|---|
| Skill bundle | the prose protocol and the two scripts | read by the agent harness, run as commands |
| Export container | the draw.io desktop CLI, headless | Docker, image `rlespinasse/drawio-export:v4.60.0` |
| Fixture corpus | the diagrams the exporter's behaviour was measured on | files under `tests/fixtures/` |
