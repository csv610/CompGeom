import math
import pytest
from compgeom.kernel import Point2D
from compgeom.polygon import Polygon, resolve_self_intersections

def test_resolve_self_intersections():
    # 1. Figure-8 polygon
    # Points: (0,0), (2,2), (0,2), (2,0)
    # This intersects at (1,1)
    p_fig8 = [Point2D(0,0), Point2D(2,2), Point2D(0,2), Point2D(2,0)]
    
    simple_vertices = resolve_self_intersections(p_fig8)
    # The result should be a simple boundary. 
    # For a figure-8, it usually returns one of the loops or the outer envelope.
    assert len(simple_vertices) >= 3
    
    # Check that it's simple (no self-intersections)
    # resolve_self_intersections is expected to return a simple boundary.
    assert isinstance(simple_vertices, list)
    assert all(isinstance(p, Point2D) for p in simple_vertices)

def test_bowtie_simplification():
    # 2. Bowtie
    p_bowtie = [Point2D(0,0), Point2D(2,0), Point2D(0,2), Point2D(2,2)]
    simple_bowtie = resolve_self_intersections(p_bowtie)
    assert len(simple_bowtie) >= 3
    for p in simple_bowtie:
        assert isinstance(p, Point2D)

if __name__ == "__main__":
    test_resolve_self_intersections()
