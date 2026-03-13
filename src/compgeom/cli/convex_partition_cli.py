from __future__ import annotations

import argparse

from compgeom import hertel_mehlhorn
from compgeom.cli._shared import demo_polygon


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Partition a demo polygon into convex pieces.")
    parser.parse_args(argv)
    points = demo_polygon()
    partitions, polygon = hertel_mehlhorn(points)
    print(f"Polygon partitioned into {len(partitions)} convex pieces.")
    for index, partition in enumerate(partitions):
        print(f"Partition {index}: {sorted(partition)}")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
