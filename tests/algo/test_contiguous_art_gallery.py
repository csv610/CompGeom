
import pytest
from compgeom.kernel import Point2D
from compgeom.polygon.polygon import Polygon
from compgeom.algo.contiguous_art_gallery import ContiguousArtGallery

def test_contiguous_art_gallery_square():
    # A simple square
    poly = Polygon(vertices=[Point2D(0, 0), Point2D(1, 0), Point2D(1, 1), Point2D(0, 1)])
    solver = ContiguousArtGallery(poly)
    guards = solver.solve()
    assert len(guards) >= 1
    # For a square, one guard in the center is enough
    # The current implementation returns centers of convex decomposition pieces.

def test_contiguous_art_gallery_l_shape():
    # L-shape polygon
    vertices = [
        Point2D(0, 0), Point2D(2, 0), Point2D(2, 1), 
        Point2D(1, 1), Point2D(1, 2), Point2D(0, 2)
    ]
    poly = Polygon(vertices=vertices)
    solver = ContiguousArtGallery(poly)
    guards = solver.solve()
    assert len(guards) >= 1

def test_connect_centers_empty():
    poly = Polygon(vertices=[Point2D(0, 0), Point2D(1, 0), Point2D(1, 1), Point2D(0, 1)])
    solver = ContiguousArtGallery(poly)
    assert solver._connect_centers([]) == []
