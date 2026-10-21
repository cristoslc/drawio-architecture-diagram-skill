# Event contracts

The events this repository publishes, and where each one is specified.

The skill has no service boundary and no external consumer, so there is no cross-boundary payload to put in a contract file. The events are workflow steps inside one repository, and they are specified as a table in [`../DOMAIN-EVENTS.md`](../DOMAIN-EVENTS.md): what produces each event, what consumes it, and what it carries.

A contract file belongs here when an event leaves this repository and a consumer outside it has to rely on the payload's shape.
