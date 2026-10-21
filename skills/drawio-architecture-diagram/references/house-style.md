# House style

The rules that make two architecture diagrams look like the same product. Follow them exactly. A diagram that ignores these is a defect even when it is accurate.

## Palette

| Role | Colour | Used for |
|---|---|---|
| Service fill | `#FFFFFF` | the default shape fill |
| Service border | `#6366F1` | the default shape border, 2px |
| Service text | `#1E293B` | the label inside a shape |
| Cluster fill | `#F8FAFC` | the container fill |
| Cluster border | `#CBD5E1` | the container border |
| Cluster text | `#64748B` | the container title, 13px bold |
| Platform fill | `#ECFDF5` | a shape that is infrastructure rather than a service |
| Platform border | `#10B981` | the border on such a shape, 2px |
| Datastore fill | `#FFF7ED` | a datastore or ledger shape |
| Datastore border | `#F97316` | the border on such a shape, 2px |
| Edge stroke | `#475569` | every edge, 2px |
| Edge text | `#475569` | the edge label, 12px |
| Label plate | `#FFFFFF` | the background behind an edge label |

Dark text on a light fill, one accent colour for services, one green for infrastructure, one orange for datastores. Nothing else. A diagram with a fourth accent colour is a diagram with no house style.

## Type

- Helvetica everywhere: on shape labels, on edge labels and on container titles.
- 14px for a shape label.
- 13px bold for a container title.
- 12px for an edge label.

## Shapes

A service or a process:

```
rounded=1;whiteSpace=wrap;html=1;fillColor=#FFFFFF;strokeColor=#6366F1;strokeWidth=2;fontSize=14;fontColor=#1E293B;fontFamily=Helvetica;arcSize=12
```

A platform shape, the same but green:

```
rounded=1;whiteSpace=wrap;html=1;fillColor=#ECFDF5;strokeColor=#10B981;strokeWidth=2;fontSize=14;fontColor=#1E293B;fontFamily=Helvetica;arcSize=12
```

A datastore:

```
shape=cylinder3;whiteSpace=wrap;html=1;boundedLbl=1;backgroundOutline=1;fillColor=#FFF7ED;strokeColor=#F97316;strokeWidth=2;fontSize=14;fontColor=#1E293B;fontFamily=Helvetica
```

A container, with the title at the top left:

```
rounded=1;whiteSpace=wrap;html=1;fillColor=#F8FAFC;strokeColor=#CBD5E1;dashed=0;verticalAlign=top;align=left;spacingLeft=14;spacingTop=8;fontSize=13;fontColor=#64748B;fontStyle=1;fontFamily=Helvetica
```

An edge, with a label that keeps its own background plate:

```
edgeStyle=orthogonalEdgeStyle;rounded=1;html=1;strokeColor=#475569;strokeWidth=2;endArrow=block;endFill=1;fontSize=12;fontColor=#475569;fontFamily=Helvetica;labelBackgroundColor=#FFFFFF
```

## Spacing

| Rule | Value |
|---|---|
| Grid | every shape's position and size is a multiple of 10 |
| Shape size | 160 to 180 wide by 60 high, wide enough for the label on one line |
| Shape gap inside a container | 40 vertical; 20 to 70 horizontal, the wider where the pair needs breathing room |
| Container padding | at least 30 to the left and right of the shapes, at least 40 above and below, and more on the side a routed edge needs a channel |
| Container gap | at least 40 between two containers on the same row |
| Row gap | at least 40 between two rows of containers |
| Canvas margin | 40 from the left and top edges |

A container's title sits at the top left with 14px of left padding and 8px of top padding, so the first shape inside starts at least 40px below the container's top edge.

The shipped example in `examples/` measures these. A container that a routed edge passes carries extra padding on that side, and that padding is where the edge's channel runs.

## Layout

- Clusters sit in one row when they fit. A second row goes below, not beside.
- Nesting stops at one level. A shape inside a container inside a container reads as noise.
- The order inside a container is the order of the flow: clients on the left, services in the middle, platform below.
- An edge that crosses a cluster gets explicit waypoints. The routing is part of the drawing, not something the renderer decides.

## Edges

- `edgeStyle=orthogonalEdgeStyle` with right angles everywhere.
- A block arrowhead, filled, at the target.
- Every edge label carries `labelBackgroundColor=#FFFFFF`, so it stays readable where it crosses a shape.
- The plate is part of the palette, and it is pinned with the rest of it. If a diagram's colours stop being pinned, the plate stops being pinned too, as `labelBackgroundColor=none`, because a plate left light under light text is a label nobody can read.
- An edge that reaches a shape on its left face enters horizontally. An edge that reaches the top face enters vertically.
- An arrow's entry point may sit off the grid. Two arrows arriving at the same face need different heights, and a point that lands on the grid lands on the other arrow's point.
- A back edge, the one that returns a response to the left, is routed on a column of its own, clear of every shape. That column may run inside a container's padding, which is what the padding is for, but it never crosses a shape.

## What the render must not show

Look at the rendered diagram and check for these four. The validator cannot see any of them.

1. A label overlapping another shape.
2. An edge running through a shape.
3. An arrowhead landing on a container title.
4. A label that reads backwards.

The shipped example in `examples/` had one of these in its first version. The correction loop exists for that reason.
