from __future__ import annotations

import argparse

from compgeom import approximate_medial_axis
from compgeom.cli._shared import demo_polygon, format_point


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Approximate the medial axis of a demo polygon.")
    parser.add_argument("--resolution", type=float, default=0.25, help="Boundary sampling resolution.")
    args = parser.parse_args(argv)

    resolution = args.resolution
    polygon = demo_polygon()
    result = approximate_medial_axis(polygon, resolution=resolution)
    print("Approximate Medial Axis:")
    print(f"  Boundary samples: {len(result['samples'])}")
    print(f"  Axis nodes:       {len(result['centers'])}")
    print(f"  Axis segments:    {len(result['segments'])}")
    for index, (start, end) in enumerate(result["segments"], start=1):
        print(f"  {index:3}: {format_point(start)} -> {format_point(end)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
