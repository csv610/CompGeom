"""Visualization helpers for geometric data."""

from __future__ import annotations

from typing import List, Tuple


def generate_svg_path(
    indices: List[int],
    width: int,
    height: int,
    cell_size: int = 20,
    stroke_color: str = "red",
    stroke_width: int = 2,
) -> str:
    """Generate an SVG string representing the path through grid cell indices."""
    if not indices:
        return ""

    svg_width = width * cell_size
    svg_height = height * cell_size

    def to_coords(idx):
        # Grid is bottom to top, left to right
        # SVG is top to bottom, left to right
        ix = idx % width
        iy = idx // width
        # Flip Y for SVG (top-left is 0,0)
        return (ix * cell_size + cell_size // 2, (height - 1 - iy) * cell_size + cell_size // 2)

    points = [to_coords(idx) for idx in indices]
    path_data = "M " + " L ".join(f"{x},{y}" for x, y in points)

    svg = [
        f'<svg width="{svg_width}" height="{svg_height}" xmlns="http://www.w3.org/2000/svg">',
        f'  <rect width="100%" height="100%" fill="white" />',
        # Draw grid
        '  <g stroke="black" stroke-width="1">',
    ]

    for i in range(width + 1):
        x = i * cell_size
        svg.append(f'    <line x1="{x}" y1="0" x2="{x}" y2="{svg_height}" />')
    for i in range(height + 1):
        y = i * cell_size
        svg.append(f'    <line x1="0" y1="{y}" x2="{svg_width}" y2="{y}" />')

    svg.extend(
        [
            "  </g>",
            f'  <path d="{path_data}" fill="none" stroke="{stroke_color}" stroke-width="{stroke_width}" stroke-linejoin="round" stroke-linecap="round" />',
            "</svg>",
        ]
    )

    return "\n".join(svg)


def save_svg(svg_content: str, filename: str):
    """Save SVG content to a file."""
    with open(filename, "w") as f:
        f.write(svg_content)


def save_png(svg_content: str, filename: str):
    """Save SVG content as a PNG file using system tools (rsvg-convert or convert)."""
    import subprocess
    import tempfile
    import os

    with tempfile.NamedTemporaryFile(suffix=".svg", delete=False) as tmp:
        tmp.write(svg_content.encode("utf-8"))
        tmp_name = tmp.name

    try:
        # Try rsvg-convert first (better SVG support)
        try:
            subprocess.run(["rsvg-convert", tmp_name, "-o", filename], check=True, capture_output=True)
            return
        except (subprocess.CalledProcessError, FileNotFoundError):
            pass

        # Try ImageMagick's convert
        try:
            subprocess.run(["convert", tmp_name, filename], check=True, capture_output=True)
            return
        except (subprocess.CalledProcessError, FileNotFoundError):
            pass

        raise RuntimeError("Neither 'rsvg-convert' nor 'convert' (ImageMagick) found to generate PNG.")
    finally:
        if os.path.exists(tmp_name):
            os.remove(tmp_name)


__all__ = ["generate_svg_path", "save_png", "save_svg"]
