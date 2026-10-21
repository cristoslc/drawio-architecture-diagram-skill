# draw.io XML rules

The file format, the cell model, and how to write a style string. Everything here is what the draw.io desktop application reads, so a file written to these rules opens in draw.io and re-exports as the same diagram.

## The file shape

```xml
<mxfile host="app.diagrams.net">
  <diagram id="order-intake" name="Order Intake">
    <mxGraphModel dx="1200" dy="820" grid="1" gridSize="10" guides="1" tooltips="1" connect="1" arrows="1" fold="1" page="1" pageScale="1" pageWidth="1200" pageHeight="820" math="0" shadow="0">
      <root>
        <mxCell id="0" />
        <mxCell id="1" parent="0" />
        <mxCell id="orders" value="Order Service" style="..." vertex="1" parent="1">
          <mxGeometry x="640" y="80" width="170" height="60" as="geometry" />
        </mxCell>
        <mxCell id="e1" value="publishes order events" style="..." edge="1" parent="1" source="orders" target="bus">
          <mxGeometry relative="1" as="geometry">
            <Array as="points">
              <mxPoint x="530" y="300" />
            </Array>
          </mxGeometry>
        </mxCell>
      </root>
    </mxGraphModel>
  </diagram>
</mxfile>
```

- `mxfile` holds `diagram` elements. A diagram element holds the model, or a compressed copy of it. Write it uncompressed: a compressed diagram is base64 that a reader cannot review in a diff.
- `mxGraphModel` holds the model attributes and one `root`.
- `root` holds every cell.
- Cell `0` is the root and cell `1` is the default layer. Every other cell names `1` as its parent.

## The container is a band, not a parent

A container in this house style is a shape drawn behind the group it holds, not a draw.io parent. The shapes inside it are siblings on the default layer, and every coordinate in the file is an absolute position on the canvas.

That has one consequence worth knowing: a waypoint means the same thing as a shape position, so a route can be read against the shapes without translating between coordinate spaces. It has another: a reader who opens the file in draw.io and drags the band does not drag the shapes with it, because there is no parent-child link to follow. Move the shapes too, or reparent the group in draw.io, which is one drag.

Write the containers before the shapes they hold. draw.io draws the cells in the order they appear, so a container written after the shapes would cover them.

## The cell model

A cell carries an `id`, an optional `value` that is its label, a `style` string, and a flag.

| Attribute | Meaning |
|---|---|
| `id` | unique within the diagram. Give every cell one. |
| `value` | the label. An absent value is an empty label. |
| `style` | the appearance. See below. |
| `vertex="1"` | this cell is a shape. |
| `edge="1"` | this cell is a connection. |
| `parent` | the layer the cell sits on. Every cell here names the default layer. |
| `source` | for an edge, the cell it starts at. |
| `target` | for an edge, the cell it ends at. |

A shape carries an `mxGeometry` child with `as="geometry"` and the four numbers `x`, `y`, `width`, `height`.

An edge carries an `mxGeometry` child with `relative="1"` and, when it needs help, an `Array as="points"` child holding `mxPoint` elements. Those points are the route. They are the difference between an edge that threads a cluster and one that goes around it.

## Rules that keep the file honest

- **Every edge names real endpoints.** `source` and `target` must be ids that exist in the same diagram. An edge that names a cell that is not there is silently dropped when draw.io loads the file, and the diagram it was meant to show is missing an arrow.
- **Every shape has geometry.** A shape with no `mxGeometry` renders at nothing.
- **Coordinates are explicit.** Do not leave a shape to be placed. The agent owns the layout.
- **Waypoints are explicit** on every edge that crosses a cluster or passes near a label.
- **Ids are stable and readable.** `orders`, `bus`, `e11`. A reader who opens the file should be able to tell what a cell is.

## The style string

A style string is a semicolon separated list of `key=value` pairs. Order does not matter to draw.io, but keep the same order every time so two style strings diff cleanly.

The keys in use here:

| Key | Meaning |
|---|---|
| `rounded` | 1 for a rounded rectangle. |
| `arcSize` | the corner radius, 12 for the house shapes. |
| `whiteSpace=wrap` | wrap the label inside the shape. |
| `html=1` | the label may carry HTML. |
| `fillColor` | the fill. |
| `strokeColor` | the border. |
| `strokeWidth` | the border width, 2. |
| `fontSize`, `fontColor`, `fontFamily`, `fontStyle` | the label typography. |
| `verticalAlign=top`, `align=left` | for a container, put the title at the top left. |
| `spacingLeft`, `spacingTop` | the padding inside a container. |
| `edgeStyle=orthogonalEdgeStyle` | right-angle routing. |
| `endArrow=block`, `endFill=1` | the arrowhead. |
| `labelBackgroundColor` | the plate behind an edge label. |
| `shape=cylinder3` | a datastore. |

The house style lists the four style strings to copy. Use them as they are. Deviating from them is how a diagram stops looking like the rest.

## A cell with extra metadata

A cell that carries metadata of its own is written as a wrapper:

```xml
<mxCell id="0" />
<mxCell id="1" parent="0" />
<UserObject label="Order Service" id="orders">
  <mxCell style="..." vertex="1" parent="1">
    <mxGeometry x="640" y="80" width="170" height="60" as="geometry" />
  </mxCell>
</UserObject>
```

The wrapper holds the label and its own attributes. The cell inside holds the style and the geometry. When the inner cell carries a label of its own, draw.io drops the wrapper and keeps the inner label, so do not put a label in both places.
