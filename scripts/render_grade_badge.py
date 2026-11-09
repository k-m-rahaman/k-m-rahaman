"""Render the source provider's real grade and metrics without a progress ring.

The public render_grade_card(svg_path, fonts_dir) function returns an RGB Pillow
image. Only the layout changes; grade, values, and the commit-year label are read
from the provider SVG. This module uses Pillow and the Python standard library.
"""
from __future__ import annotations

import argparse
from pathlib import Path
import re
import xml.etree.ElementTree as ET

from PIL import Image, ImageDraw, ImageFont

WIDTH, HEIGHT, SCALE = 1200, 720, 2
PANEL = "#0F1430"
TILE = "#141E3A"
LINE = "#2B385C"
TEXT = "#F1F5FF"
MUTED = "#91A0C4"
CYAN = "#45E4FF"
VIOLET = "#A78BFA"
PINK = "#FF64C8"


def _local_tag(element: ET.Element) -> str:
    return element.tag.rsplit("}", 1)[-1]


def _text(element: ET.Element) -> str:
    return " ".join("".join(element.itertext()).split())


def parse_grade_data(svg_path: str | Path) -> dict:
    """Read explicit provider text, failing instead of inventing missing data."""
    root = ET.parse(svg_path).getroot()
    parents = {child: parent for parent in root.iter() for child in parent}
    rank = next(
        (element for element in root.iter()
         if "rank-text" in element.get("class", "").split()),
        None,
    )
    grade = _text(rank) if rank is not None else ""
    if not grade or not re.fullmatch(r"[A-Za-z0-9+\-−]{1,12}", grade):
        raise ValueError("The provider SVG has no readable grade label.")

    metrics = {}
    for key in ("stars", "commits", "prs", "issues", "contribs"):
        value_element = next(
            (element for element in root.iter()
             if element.get("data-testid") == key
             and _local_tag(element) == "text"),
            None,
        )
        if value_element is None or not _text(value_element):
            raise ValueError(f"The provider SVG is missing metric: {key}")
        siblings = list(parents.get(value_element, []))
        label_element = next(
            (element for element in siblings
             if _local_tag(element) == "text" and element is not value_element
             and _text(element)),
            None,
        )
        if label_element is None:
            raise ValueError(f"The provider SVG is missing the label for: {key}")
        label = _text(label_element).rstrip(":").strip()
        # Preserve the source's year and meaning while shortening repeated words.
        if label.startswith("Total "):
            label = label[6:]
        metrics[key] = {"label": label, "value": _text(value_element)}
    return {"grade": grade, "metrics": metrics}


def render_grade_card(svg_path: str | Path, fonts_dir: str | Path) -> Image.Image:
    """Return the ring-free 1200×720 grade card, using bundled OFL fonts."""
    data = parse_grade_data(svg_path)
    fonts_dir = Path(fonts_dir)
    canvas = Image.new("RGB", (WIDTH * SCALE, HEIGHT * SCALE), PANEL)
    draw = ImageDraw.Draw(canvas)

    def font(size, weight=500, mono=False):
        filename = "JetBrainsMono.ttf" if mono else "Manrope.ttf"
        result = ImageFont.truetype(str(fonts_dir / filename), round(size * SCALE))
        try:
            axes = result.get_variation_axes()
            result.set_variation_by_axes([
                weight if axis["name"] == b"Weight" else axis["default"]
                for axis in axes
            ])
        except (OSError, AttributeError):
            pass
        return result

    def text(x, y, value, size, color=TEXT, weight=500, mono=False, anchor=None):
        draw.text(
            (round(x * SCALE), round(y * SCALE)), str(value),
            font=font(size, weight, mono), fill=color, anchor=anchor,
        )

    def rect(bounds, fill, outline=None, radius=20, width=1):
        draw.rounded_rectangle(
            tuple(round(value * SCALE) for value in bounds),
            radius=round(radius * SCALE), fill=fill, outline=outline,
            width=round(width * SCALE),
        )

    def fit_text(value, maximum, initial_size, weight=700):
        size = initial_size
        while size > 24 and draw.textlength(str(value), font=font(size, weight)) > maximum * SCALE:
            size -= 1
        return size

    # Header: a rectangular typographic grade badge, without circular geometry.
    text(44, 43, "My GitHub stats", 46, TEXT, 750)
    text(47, 111, "Public GitHub activity", 29, MUTED)
    text(47, 170, "GITHUB README STATS", 21, VIOLET, 500, True)

    rect((936, 34, 1156, 208), "#1C2041", "#5E5696", 24, 2)
    text(1046, 65, "GRADE", 24, VIOLET, 600, True, "mm")
    grade_size = fit_text(data["grade"], 184, 84, 800)
    text(1046, 134, data["grade"], grade_size, CYAN, 800, anchor="mm")

    draw.line((44 * SCALE, 238 * SCALE, 1156 * SCALE, 238 * SCALE), fill=LINE, width=SCALE)

    # Values are kept large enough to read when this card shares a README row.
    positions = [
        ("stars", 44, 266, CYAN),
        ("commits", 612, 266, VIOLET),
        ("prs", 44, 438, PINK),
        ("issues", 612, 438, CYAN),
    ]
    for key, x, y, color in positions:
        metric = data["metrics"][key]
        rect((x, y, x + 544, y + 150), TILE, LINE, 18)
        rect((x + 22, y + 25, x + 27, y + 52), color, radius=2)
        label_size = fit_text(metric["label"], 458, 28, 600)
        text(x + 44, y + 23, metric["label"], label_size, MUTED, 600)
        value_size = fit_text(metric["value"], 490, 59, 750)
        text(x + 26, y + 70, metric["value"], value_size, TEXT, 750)

    contributed = data["metrics"]["contribs"]
    rect((44, 612, 1156, 688), "#121B34", LINE, 16)
    text(70, 650, contributed["label"], 28, MUTED, 600, anchor="lm")
    text(1126, 650, contributed["value"], 44, CYAN, 750, anchor="rm")

    return canvas.resize((WIDTH, HEIGHT), Image.Resampling.LANCZOS)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--svg", type=Path, required=True)
    parser.add_argument("--fonts", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    image = render_grade_card(args.svg, args.fonts)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    image.save(args.output, optimize=True)
    print(f"Rendered provider grade {parse_grade_data(args.svg)['grade']} without a ring: {args.output}")


if __name__ == "__main__":
    main()
