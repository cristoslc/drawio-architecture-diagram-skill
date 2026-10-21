#!/usr/bin/env python3
"""Check that every committed .drawio.svg carries the diagram of its .drawio source.

A .drawio.svg is the reader-facing artifact. It renders inline in GitHub
Markdown, and it reopens in draw.io with the diagram intact, because the XML
travels inside the SVG root `content` attribute. That only holds if the
artifact is regenerated when the source changes, so this check compares the
embedded XML against the sibling .drawio file.

Both sides are read as draw.io reads a diagram, not as XML text. The draw.io
exporter re-serialises the diagram from its own model, so the XML on the two
sides never matches byte for byte: the attribute order changes, the exporter
stamps its own `host` on the `mxfile` element, and it writes a cell's
attributes in its own order. Reading both sides as a model cancels all of that
out and leaves only what a reader would see.

The model reader follows draw.io's own rules, each established by rendering a
hand-built diagram through the real export and diffing the embedded XML:

- a cell's `value` is its label, and a cell with no label has an empty one;
- a flag attribute that sits at draw.io's default is dropped from the export,
  so an absent attribute and one spelled out at the default read the same.
  The defaults are `collapsed`, `edge`, and `vertex` false, and `connectable`
  and `visible` true;
- a cell's geometry is the `mxGeometry` child that carries `as="geometry"`.
  A cell can hold more than one geometry child, and the exporter writes them
  in a different order than the source does, so the geometry is chosen by its
  `as` attribute and not by position. A geometry child with no `as` attribute
  is not the cell's geometry at all, and draw.io drops it;
- a cell written as a `UserObject` or `object` wrapper holds its label and
  its own attributes, while the `mxCell` inside it holds the style and the
  geometry. When the inner cell carries a label of its own, draw.io drops the
  wrapper and keeps the inner label, so the reader does the same. A wrapper
  with no inner cell at all is read as a wrapper with an empty inner cell,
  because draw.io writes one for it.

A source may also be a compressed diagram, where the `diagram` element holds
the model percent-escaped, deflated, and base64-encoded instead of the model
itself. draw.io writes it that way and reads it back the same way, so this
check does too.

The rules are locked down by the fixture self-test in `--self-test`, which
runs the comparison over the diagrams the exporter was measured on, then over
deliberately damaged copies.

Usage: python3 scripts/validate-drawio-svg.py <directory>
       python3 scripts/validate-drawio-svg.py --self-test

The directory is walked for committed .drawio.svg files, and each one is
compared against the .drawio file beside it.
"""

import base64
import binascii
import os
import sys
import tempfile
import urllib.parse
import xml.etree.ElementTree as ET
import zlib

def fixture_directory():
    """Find the fixture diagrams, wherever this copy of the script sits.

    A consumer who vendors the skill into their own repository has the
    fixtures next to the script, and the ones in this repository live under
    tests/fixtures. Both layouts are searched, and DRAWDIO_SVG_FIXTURES
    overrides both.
    """
    override = os.environ.get("DRAWDIO_SVG_FIXTURES")
    if override:
        return override

    here = os.path.dirname(os.path.abspath(__file__))
    candidates = (
        os.path.join(here, "fixtures"),
        os.path.join(here, "fixtures", "drawio-svg"),
        os.path.join(here, "..", "..", "..", "tests", "fixtures"),
    )
    for candidate in candidates:
        if os.path.isdir(candidate):
            return os.path.normpath(candidate)
    return os.path.normpath(candidates[0])


FIXTURE_DIRECTORY = fixture_directory()

CELL_TAGS = ("mxCell", "UserObject", "object")
GEOMETRY_NUMERIC = ("x", "y", "width", "height")

# The attributes of the model element a reader sees. draw.io rewrites the
# rest of them on export, so only these are compared. Each one has a
# default, and the exporter writes that default out, so an absent attribute
# and an attribute spelled out at its default read the same.
MODEL_ATTRIBUTES = {
    "background": None,
    "shadow": "0",
    "math": "0",
    "pageScale": "1",
}

# The page size is a pair, and draw.io fills the whole pair in when either
# half is missing. A source that carries only a width has that width
# discarded on export, so the pair reads as draw.io's own default.
PAGE_SIZE_DEFAULTS = ("850", "1100")

# The two cells every diagram opens with: the root cell and the default layer.
# They are structure rather than content, and draw.io drops them from a
# diagram that holds nothing but wrapper cells, so they are not compared.
STRUCTURAL_CELL_IDS = ("0", "1")

# The attributes draw.io's model gives a default value. A cell that spells
# one out at its default reads the same as a cell that leaves it out, because
# the exporter drops it.
MODEL_DEFAULTS = {
    "value": "",
    "style": "",
    "tooltip": "",
    "collapsed": "0",
    "connectable": "1",
    "vertex": "0",
    "edge": "0",
    "visible": "1",
}


def number_of(text):
    """Return a geometry number as a number.

    draw.io parses a coordinate as a number and writes it back in its own
    canonical form, so a source that writes `10.0` or `4e1` produces an
    artifact that writes `10` and `40`. The comparison is on the numbers.
    """
    try:
        return float(text)
    except (TypeError, ValueError):
        return text


def attributes_of(element):
    """Return a cell element's attributes with draw.io's defaults filled in."""
    attributes = {
        key: value for key, value in element.attrib.items() if key != "id"
    }
    for key, default in MODEL_DEFAULTS.items():
        attributes.setdefault(key, default)
    return attributes


def geometry_of(element):
    """Return the comparable form of a cell's geometry children.

    A cell can hold more than one geometry child. The one that counts is the
    one carrying `as="geometry"`, and it is chosen by that attribute because
    the exporter writes the children in a different order than the source.
    A geometry child with no `as` attribute is not the cell's geometry, and
    draw.io drops it. A cell can also hold more than one array of waypoints,
    and draw.io keeps the last one.
    """
    if element is None:
        return {}

    geometries = {}
    for geometry_element in element.findall("mxGeometry"):
        kind = geometry_element.get("as")
        if kind is None:
            continue

        attributes = {
            name: number_of(geometry_element.get(name, "0")) for name in GEOMETRY_NUMERIC
        }
        attributes["relative"] = number_of(geometry_element.get("relative", "0"))

        waypoints = []
        source_point = None
        target_point = None
        offset = None

        # A cell can hold more than one array of waypoints, and draw.io keeps
        # the last one. A point inside an array that is tagged as an endpoint
        # is the edge's endpoint, not a waypoint.
        arrays = geometry_element.findall("Array")
        if arrays:
            for point in arrays[-1].findall("mxPoint"):
                if point.get("as") == "sourcePoint":
                    source_point = (number_of(point.get("x", "0")), number_of(point.get("y", "0")))
                elif point.get("as") == "targetPoint":
                    target_point = (number_of(point.get("x", "0")), number_of(point.get("y", "0")))
                else:
                    waypoints.append((number_of(point.get("x", "0")), number_of(point.get("y", "0"))))

        for point in geometry_element.findall("mxPoint"):
            if point.get("as") == "sourcePoint":
                source_point = (number_of(point.get("x", "0")), number_of(point.get("y", "0")))
            elif point.get("as") == "targetPoint":
                target_point = (number_of(point.get("x", "0")), number_of(point.get("y", "0")))
            elif point.get("as") == "offset":
                # Where a dragged label sits, which moves the label without
                # moving the shape.
                offset = (number_of(point.get("x", "0")), number_of(point.get("y", "0")))

        geometries[kind] = {
            "attributes": attributes,
            "waypoints": waypoints,
            "sourcePoint": source_point,
            "targetPoint": target_point,
            "offset": offset,
        }
    return geometries


def decode_compressed_diagram(diagram):
    """Return the mxGraphModel of a compressed diagram element, or None.

    draw.io writes a compressed diagram the way its own reader expects it:
    the model is percent-escaped, then deflated raw, then base64-encoded.
    The reader inflates the bytes and then percent-decodes them, so this does
    the same in the same order.
    """
    text = (diagram.text or "").strip()
    if not text:
        return None

    try:
        raw = base64.b64decode(text, validate=False)
    except (binascii.Error, ValueError) as error:
        raise ValueError(f"the compressed diagram is not valid base64: {error}")

    inflated = None
    for wbits in (-zlib.MAX_WBITS, zlib.MAX_WBITS):
        try:
            inflated = zlib.decompress(raw, wbits)
            break
        except zlib.error:
            continue
    if inflated is None:
        raise ValueError("the compressed diagram does not decompress")

    return ET.fromstring(urllib.parse.unquote(inflated.decode("utf-8")))


def model_of(diagram):
    """Return the mxGraphModel element of one diagram element, or None."""
    if diagram.tag == "mxGraphModel":
        return diagram

    model = diagram.find("mxGraphModel")
    if model is None:
        model = decode_compressed_diagram(diagram)
    return model


def root_of(diagram):
    """Return the <root> element holding the cells of one diagram element."""
    model = model_of(diagram)
    if model is None:
        return None
    return model.find("root")

def diagrams_of(root):
    """Return the diagram elements of a parsed .drawio file."""
    if root.tag == "mxfile":
        return root.findall("diagram")
    if root.tag == "mxGraphModel":
        return [root]
    return [root]


def cell_signature(element):
    """Return the comparable signature of one cell element, or None if it has no id."""
    cell_id = element.get("id")
    if cell_id is None:
        return None

    inner = element.find("mxCell") if element.tag != "mxCell" else None

    if element.tag == "mxCell":
        # A plain cell. Everything it carries is its own.
        return cell_id, {
            "kind": "cell",
            "outer": attributes_of(element),
            "inner": None,
            "geometry": geometry_of(element),
        }

    if inner is None:
        # A wrapper with no inner cell. draw.io writes one for it anyway.
        return cell_id, {
            "kind": "wrapper",
            "outer": attributes_of(element),
            "inner": dict(MODEL_DEFAULTS),
            "geometry": {},
        }

    if inner.get("value") is not None:
        # A wrapper whose inner cell carries a label of its own. draw.io drops
        # the wrapper and keeps the inner cell, so the reader does the same.
        return cell_id, {
            "kind": "cell",
            "outer": attributes_of(inner),
            "inner": None,
            "geometry": geometry_of(inner),
        }

    # A wrapper. The label and the wrapper's own attributes sit on the
    # wrapper, the style and the geometry on the inner cell.
    return cell_id, {
        "kind": "wrapper",
        "outer": attributes_of(element),
        "inner": attributes_of(inner),
        "geometry": geometry_of(inner),
    }


def cell_elements(root):
    """Yield the elements that carry a cell, wrappers included.

    A `UserObject` or `object` wrapper holds the cell's id and label, and the
    inner `mxCell` holds its style and geometry. The inner cell has no id of
    its own, so it is skipped here and read through its wrapper.
    """
    wrapped = set()
    for element in root.iter():
        if element.tag in ("UserObject", "object"):
            inner = element.find("mxCell")
            if inner is not None:
                wrapped.add(id(inner))

    for element in root.iter():
        if element.tag in CELL_TAGS and id(element) not in wrapped:
            yield element


def drop_dangling_references(cells, known_ids):
    """Drop a reference to a cell that does not exist in the same diagram.

    draw.io drops a cell's parent, and an edge's source and target, when the
    cell they name does not exist, so a source with a dangling reference reads
    the same as the artifact, where the attribute is gone. The rule covers
    both halves of a wrapper, since the inner cell carries its own parent.
    """
    for signature in cells.values():
        for half in ("outer", "inner"):
            attributes = signature[half]
            if attributes is None:
                continue
            for reference in ("parent", "source", "target"):
                named = attributes.get(reference)
                if named is not None and named not in known_ids:
                    del attributes[reference]
    return cells


def cells_of(diagram):
    """Return (cells by id, cells without an id, duplicate ids) for one diagram."""
    root = root_of(diagram)
    cells = {}
    without_id = []
    duplicates = []
    if root is None:
        return cells, without_id, duplicates

    for element in cell_elements(root):
        result = cell_signature(element)
        if result is None:
            without_id.append(element.tag)
            continue
        cell_id, signature = result
        if cell_id in cells:
            duplicates.append(cell_id)
            continue
        cells[cell_id] = signature
    for structural_id in STRUCTURAL_CELL_IDS:
        cells.pop(structural_id, None)
    return cells, without_id, duplicates


def model_signature(diagram):
    """Return the reader-visible attributes of a diagram's model element.

    draw.io rewrites most of the model attributes on export, so only the
    ones a reader can see are compared: the page background, the shadow, the
    maths setting, and the page size.
    """
    try:
        model = model_of(diagram)
    except (ET.ParseError, ValueError):
        return {}
    if model is None:
        return {}

    signature = {}
    for name, default in MODEL_ATTRIBUTES.items():
        value = model.get(name, default)
        if value is None or value == "":
            # An attribute the exporter drops, either because it was absent
            # or because it was empty.
            continue
        # The page scale is a number, and the exporter writes it back in its
        # own canonical form, so a source that writes 1.0 and an artifact
        # that writes 1 are the same value.
        signature[name] = number_of(value) if name == "pageScale" else value

    width = model.get("pageWidth")
    height = model.get("pageHeight")
    if width is None or width == "" or height is None or height == "":
        width, height = PAGE_SIZE_DEFAULTS
    signature["pageWidth"] = number_of(width)
    signature["pageHeight"] = number_of(height)

    return signature


def known_ids_of(diagram):
    """Return the ids every cell in a diagram carries, structural ones included."""
    try:
        root = root_of(diagram)
    except (ET.ParseError, ValueError):
        return set()
    if root is None:
        return set()
    return {
        element.get("id")
        for element in cell_elements(root)
        if element.get("id") is not None
    }


def cells_of_diagram(diagram, label):
    """Return the cells of one diagram, turning a broken diagram into problems."""
    try:
        return cells_of(diagram), []
    except ET.ParseError as error:
        return ({}, [], []), [f"the {label} diagram does not parse: {error}"]
    except ValueError as error:
        return ({}, [], []), [f"the {label} diagram cannot be read: {error}"]

def embedded_xml(svg_path):
    """Return the diagram XML embedded in the SVG root content attribute."""
    root = ET.parse(svg_path).getroot()
    return root.get("content")


def describe(value):
    if value is None:
        return "nothing"
    if isinstance(value, dict):
        return "{" + ", ".join(f"{k}={v}" for k, v in sorted(value.items())) + "}"
    return repr(value)


def check_pair(source_path, svg_path):
    """Return a list of problem strings for one source and artifact pair."""
    try:
        source_root = ET.parse(source_path).getroot()
    except ET.ParseError as error:
        return [f"the source .drawio does not parse: {error}"]

    try:
        embedded = embedded_xml(svg_path)
    except ET.ParseError as error:
        return [f"the SVG is not well-formed XML: {error}"]

    if embedded is None:
        return ["the SVG root carries no content attribute, so draw.io cannot recover the diagram"]

    try:
        embedded_root = ET.fromstring(embedded)
    except ET.ParseError as error:
        return [f"the embedded diagram XML does not parse: {error}"]

    source_diagrams = diagrams_of(source_root)
    embedded_diagrams = diagrams_of(embedded_root)

    if not source_diagrams:
        return ["the source .drawio holds no diagram, so it cannot be compared"]
    if not embedded_diagrams:
        return ["the SVG carries no diagram, so it cannot be compared"]

    if len(source_diagrams) > len(embedded_diagrams):
        return [
            f"the source has {len(source_diagrams)} pages and the SVG carries "
            f"{len(embedded_diagrams)}, so the artifact cannot cover the whole source. "
            "The render script handles a single-page diagram."
        ]

    problems = []

    for index, source_diagram in enumerate(source_diagrams):
        embedded_diagram = embedded_diagrams[index] if index < len(embedded_diagrams) else None
        if embedded_diagram is None:
            problems.append(
                f"the source has a page the SVG does not carry: "
                f"{page_name(source_diagram)}"
            )
            continue
        problems.extend(compare_pages(source_diagram, embedded_diagram, index))

    for index, embedded_diagram in enumerate(embedded_diagrams):
        if index >= len(source_diagrams):
            problems.append(
                f"the SVG carries a page the source does not have: {page_name(embedded_diagram)}"
            )

    return problems


def page_name(diagram):
    """Return the name of a diagram element, for a message."""
    return diagram.get("name") or diagram.get("id") or "an unnamed page"


def compare_pages(source_diagram, embedded_diagram, index):
    """Return the problems found between one source page and one embedded page."""
    (source_cells, source_without_id, source_duplicates), source_problems = cells_of_diagram(
        source_diagram, f"source page {index + 1}"
    )
    (embedded_cells, embedded_without_id, embedded_duplicates), embedded_problems = cells_of_diagram(
        embedded_diagram, f"embedded page {index + 1}"
    )

    problems = list(source_problems) + list(embedded_problems)

    # A reference to a cell that exists in neither page is dropped by draw.io,
    # so it is dropped here too. The ids of both pages count, because the
    # exporter drops the structural cells of a diagram that holds nothing but
    # wrapper cells.
    known_ids = known_ids_of(source_diagram) | known_ids_of(embedded_diagram)
    drop_dangling_references(source_cells, known_ids)
    drop_dangling_references(embedded_cells, known_ids)

    if source_duplicates:
        problems.append(
            "the source has cells with a duplicate id: " + ", ".join(sorted(set(source_duplicates)))
        )
    if source_without_id:
        problems.append(
            f"the source has {len(source_without_id)} cell(s) with no id, so they cannot be "
            "matched against the SVG. Give every cell an id."
        )
    if embedded_without_id:
        problems.append(
            f"the SVG has {len(embedded_without_id)} cell(s) with no id, so they cannot be "
            "matched against the source."
        )
    if embedded_duplicates:
        problems.append(
            "the SVG has cells with a duplicate id: " + ", ".join(sorted(set(embedded_duplicates)))
        )

    if not source_cells:
        return problems or ["the source holds no readable mxCell elements, so it cannot be compared"]

    missing = [cell_id for cell_id in source_cells if cell_id not in embedded_cells]
    if missing:
        problems.append("cells missing from the SVG: " + ", ".join(sorted(missing)))

    extra = [cell_id for cell_id in embedded_cells if cell_id not in source_cells]
    if extra:
        problems.append("cells in the SVG that are not in the source: " + ", ".join(sorted(extra)))

    source_model = model_signature(source_diagram)
    embedded_model = model_signature(embedded_diagram)
    if source_model != embedded_model:
        problems.append(
            f"the diagram model differs: source has {describe(source_model)}, "
            f"the SVG has {describe(embedded_model)}"
        )

    # The page name is what draw.io shows on its page tab, and the page id is
    # what draw.io writes into the file name it saves, so a reader sees both.
    # The exporter keeps the name and the id of a page the source carries
    # them for, and it refuses a source that names no page at all, so both
    # are only compared when the source carries one.
    for attribute in ("name", "id"):
        source_value = source_diagram.get(attribute)
        embedded_value = embedded_diagram.get(attribute)
        if source_value is not None and source_value != embedded_value:
            problems.append(
                f"the page {attribute} differs: the source calls it "
                f"{source_value!r}, the SVG calls it {embedded_value!r}"
            )

    for cell_id in sorted(set(source_cells) & set(embedded_cells)):
        source_signature = source_cells[cell_id]
        embedded_signature = embedded_cells[cell_id]
        for attribute in ("kind", "outer", "inner", "geometry"):
            if source_signature[attribute] != embedded_signature[attribute]:
                problems.append(
                    f"cell {cell_id} differs in {attribute}: "
                    f"source has {describe(source_signature[attribute])}, "
                    f"the SVG has {describe(embedded_signature[attribute])}"
                )

    return problems


def fixture_pairs():
    """Return the (name, source, artifact) fixture triples, in name order."""
    triples = []
    for name in sorted(os.listdir(FIXTURE_DIRECTORY)):
        if not name.endswith(".drawio"):
            continue
        source = os.path.join(FIXTURE_DIRECTORY, name)
        artifact = os.path.join(FIXTURE_DIRECTORY, name[: -len(".drawio")] + ".drawio.svg")
        triples.append((name, source, artifact))
    return triples


def damage_cases():
    """Return the (description, fixture, mutation, expected) cases for the self-test."""
    return (
        ("renamed cell", "plain", "renamed", ("cells in the SVG that are not in the source: a",)),
        ("changed label", "plain", "label", ("cell a differs in outer",)),
        ("changed style", "plain", "style", ("cell a differs in outer",)),
        ("moved shape", "plain", "moved", ("cell a differs in geometry",)),
        ("deleted cell", "edge", "deleted", ("cells in the SVG that are not in the source: a",)),
        ("added cell", "plain", "added", ("cells missing from the SVG: a2",)),
        ("changed tooltip", "tooltip", "tooltip", ("cell a differs in outer",)),
        ("changed collapsed flag", "attrs", "collapsed", ("cell a differs in outer",)),
        ("changed connectable flag", "attrs", "connectable", ("cell b differs in outer",)),
        ("changed visible flag", "attrs", "visible", ("cell a differs in outer",)),
        ("changed edge endpoint", "edge", "rewired", ("cell e differs in outer",)),
        ("changed edge waypoint", "waypoints", "waypoint", ("cell e differs in geometry",)),
        ("changed wrapper label", "wrapper", "wraplabel", ("cell w differs in outer",)),
        ("changed wrapper attribute", "wrapper", "wrapattr", ("cell w differs in outer",)),
        ("renamed page", "plain", "pagename", ("the page name differs",)),
        ("changed page size", "plain", "pagesize", ("the diagram model differs",)),
        ("changed page background", "bg1", "background", ("the diagram model differs",)),
        ("changed page scale", "pagescale", "pagescale", ("the diagram model differs",)),
        ("moved label offset", "labeloffset", "offset", ("cell a differs in geometry",)),
    )


def apply_mutation(text, mutation):
    """Return the source text with one deliberate change applied."""
    if mutation == "renamed":
        return text.replace('id="a"', 'id="a2"')
    if mutation == "label":
        return text.replace('value="A"', 'value="A2"')
    if mutation == "style":
        return text.replace('style="rounded=0;"', 'style="rounded=1;"')
    if mutation == "moved":
        return text.replace('x="10"', 'x="70"')
    if mutation == "rewired":
        return text.replace('source="a"', 'source="b"')
    if mutation == "deleted":
        start = text.index('<mxCell id="a"')
        end = text.index("</mxCell>", start) + len("</mxCell>")
        return text[:start] + text[end:]
    if mutation == "added":
        return text.replace(
            "</root>",
            '<mxCell id="a2" value="B" style="rounded=0;" vertex="1" parent="1">'
            '<mxGeometry x="200" y="10" width="60" height="40" as="geometry" /></mxCell></root>',
        )
    if mutation == "tooltip":
        return text.replace('tooltip="tip"', 'tooltip="other"')
    if mutation == "collapsed":
        return text.replace('collapsed="0"', 'collapsed="1"')
    if mutation == "connectable":
        return text.replace('connectable="0"', 'connectable="1"')
    if mutation == "visible":
        return text.replace('visible="1"', 'visible="0"')
    if mutation == "waypoint":
        return text.replace('<mxPoint x="130" y="120" />', '<mxPoint x="140" y="120" />')
    if mutation == "wraplabel":
        return text.replace('label="L"', 'label="M"')
    if mutation == "wrapattr":
        return text.replace('fillColor="#dae8fc"', 'fillColor="#ff0000"')
    if mutation == "pagename":
        return text.replace('name="Page-1"', 'name="Renamed page"')
    if mutation == "pagesize":
        return text.replace('pageWidth="850"', 'pageWidth="1200"')
    if mutation == "background":
        return text.replace('background="#FF0000"', 'background="#00FF00"')
    if mutation == "pagescale":
        return text.replace('pageScale="1.0"', 'pageScale="2"')
    if mutation == "offset":
        return text.replace('<mxPoint as="offset" x="12" y="8" />', '<mxPoint as="offset" x="40" y="8" />')
    raise ValueError(f"unknown mutation: {mutation}")


def corner_cases():
    """Return the (description, source text, artifact text, expected) cases that must fail loudly."""
    plain = open(os.path.join(FIXTURE_DIRECTORY, "plain.drawio"), encoding="utf-8").read()
    artifact = open(os.path.join(FIXTURE_DIRECTORY, "plain.drawio.svg"), encoding="utf-8").read()

    # A compressed diagram whose payload is not valid base64, and one whose
    # payload does not decompress. Both used to abort the whole run with a
    # stack trace instead of naming the file.
    broken_base64 = '<mxfile host="app.diagrams.net"><diagram id="d1" name="Page-1">not base64!!</diagram></mxfile>'
    broken_deflate = (
        '<mxfile host="app.diagrams.net"><diagram id="d1" name="Page-1">'
        + base64.b64encode(b"not a deflate stream").decode()
        + "</diagram></mxfile>"
    )

    return (
        ("a source that is not XML", "not xml at all", artifact, "does not parse"),
        ("an artifact that is not well-formed", plain, "<svg>", "not well-formed XML"),
        (
            "an artifact with no content attribute",
            plain,
            '<?xml version="1.0"?><svg xmlns="http://www.w3.org/2000/svg"></svg>',
            "no content attribute",
        ),
        ("a compressed source that is not base64", broken_base64, artifact, "cannot be read"),
        ("a compressed source that does not decompress", broken_deflate, artifact, "cannot be read"),
    )


def self_test():
    """Run the comparison over the fixture diagrams and over deliberate damage.

    The fixtures are the diagrams the exporter's behaviour was measured on.
    Every one of them must pass, which is what keeps the comparison from
    reporting a legitimate source as stale. The damaged copies must fail,
    which is what keeps the check from passing on a stale artifact.
    """
    if not os.path.isdir(FIXTURE_DIRECTORY):
        print(f"FAIL  no fixture directory at {FIXTURE_DIRECTORY}")
        return 1

    triples = fixture_pairs()
    if not triples:
        print(f"FAIL  no fixture diagrams in {FIXTURE_DIRECTORY}")
        return 1

    failures = 0
    checked = 0

    for name, source, artifact in triples:
        if not os.path.isfile(artifact):
            print(f"FAIL  {name} :: no fixture artifact to compare against")
            failures += 1
            continue
        problems = check_pair(source, artifact)
        if problems:
            failures += 1
            print(f"FAIL  {name} :: the fixture artifact does not match its source")
            for problem in problems:
                print(f"      {problem}")
        else:
            checked += 1
            print(f"PASS  {name}")

    for description, fixture, mutation, expected in damage_cases():
        source = os.path.join(FIXTURE_DIRECTORY, f"{fixture}.drawio")
        artifact = os.path.join(FIXTURE_DIRECTORY, f"{fixture}.drawio.svg")
        with tempfile.TemporaryDirectory() as work:
            damaged = os.path.join(work, f"{fixture}.drawio")
            text = open(source, encoding="utf-8").read()
            changed = apply_mutation(text, mutation)
            if changed == text:
                failures += 1
                print(f"FAIL  {description} :: the mutation did not change the source")
                continue
            open(damaged, "w", encoding="utf-8").write(changed)
            problems = check_pair(damaged, artifact)
        report = " | ".join(problems)
        if not problems:
            failures += 1
            print(f"FAIL  {description} :: the check did not notice the damage")
        elif not all(fragment in report for fragment in expected):
            failures += 1
            print(f"FAIL  {description} :: the check reported the wrong problem")
            for problem in problems:
                print(f"      {problem}")
        else:
            checked += 1
            print(f"PASS  {description}")

    for description, source_text, artifact_text, expected in corner_cases():
        with tempfile.TemporaryDirectory() as work:
            source = os.path.join(work, "case.drawio")
            artifact = os.path.join(work, "case.drawio.svg")
            open(source, "w", encoding="utf-8").write(source_text)
            open(artifact, "w", encoding="utf-8").write(artifact_text)
            problems = check_pair(source, artifact)
        report = " | ".join(problems)
        if expected in report:
            checked += 1
            print(f"PASS  {description}")
        else:
            failures += 1
            print(f"FAIL  {description} :: the check reported the wrong problem")
            for problem in problems:
                print(f"      {problem}")

    print()
    if failures:
        print(f"RESULT: {failures} of {checked + failures} self-test(s) failed.")
        return 1
    print(f"RESULT: all {checked} self-test(s) passed.")
    return 0


def main():
    if len(sys.argv) == 2 and sys.argv[1] == "--self-test":
        return self_test()

    if len(sys.argv) != 2:
        print("Usage: python3 scripts/validate-drawio-svg.py <directory>", file=sys.stderr)
        return 2

    root = os.path.abspath(sys.argv[1])

    if not os.path.isdir(root):
        print(f"FAIL  {root} is not a directory, so there is nothing to check.")
        return 1

    pairs = []
    for dirpath, dirnames, filenames in os.walk(root):
        dirnames[:] = [name for name in dirnames if name not in {".git", ".worktrees", "node_modules"}]
        for name in sorted(filenames):
            if not name.endswith(".drawio.svg"):
                continue
            svg_path = os.path.join(dirpath, name)
            source_path = os.path.join(dirpath, name[: -len(".svg")])
            pairs.append((source_path, svg_path))

    if not pairs:
        print(f"FAIL  no committed .drawio.svg found under {root}.")
        return 1

    failures = 0
    for source_path, svg_path in sorted(pairs):
        rel_svg = os.path.relpath(svg_path, root)
        if not os.path.isfile(source_path):
            print(f"FAIL  {rel_svg} :: no sibling .drawio source to compare against")
            failures += 1
            continue
        problems = check_pair(source_path, svg_path)
        if problems:
            failures += 1
            print(f"FAIL  {rel_svg}")
            for problem in problems:
                print(f"      {problem}")
        else:
            print(f"PASS  {rel_svg}")

    print()
    if failures:
        print(f"RESULT: {failures} of {len(pairs)} committed draw.io SVG(s) are stale.")
        return 1
    print(f"RESULT: all {len(pairs)} committed draw.io SVG(s) match their source.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
