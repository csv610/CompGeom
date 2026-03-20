
import pytest
from compgeom.kernel.point import Point2D
from compgeom.kernel.geometry import clip_polygon

@pytest.fixture
def square_poly():
    """A 1x1 square polygon."""
    return [Point2D(0, 0), Point2D(1, 0), Point2D(1, 1), Point2D(0, 1)]

def tuple_set(points):
    """Converts a list of points to a set of rounded tuples for comparison."""
    return {(round(p.x, 9), round(p.y, 9)) for p in points}

def test_clip_no_intersection_all_inside(square_poly):
    """Test clipping where the polygon is entirely inside the half-plane."""
    line_start = Point2D(2, 0)
    line_end = Point2D(2, 1)
    result = clip_polygon(square_poly, line_start, line_end)
    assert len(result) == 4
    assert set(result) == set(square_poly)

def test_clip_no_intersection_all_outside(square_poly):
    """Test clipping where the polygon is entirely outside the half-plane."""
    # Line at x=-1, pointing up. "Left" half-plane is x <= -1.
    line_start = Point2D(-1, 0)
    line_end = Point2D(-1, 1)
    result = clip_polygon(square_poly, line_start, line_end)
    assert len(result) == 0

def test_clip_vertical_line(square_poly):
    """Test clipping with a vertical line through the middle."""
    line_start = Point2D(0.5, 0)
    line_end = Point2D(0.5, 1)
    result = clip_polygon(square_poly, line_start, line_end)
    
    expected_points = {
        (0, 0), (0.5, 0), (0.5, 1), (0, 1)
    }
    assert len(result) == 4
    assert tuple_set(result) == expected_points

def test_clip_diagonal_line(square_poly):
    """Test clipping with a diagonal line that cuts off a corner."""
    # Line y = -x + 1.5. "inside" is x+y <= 1.5
    line_start = Point2D(1, 0.5)
    line_end = Point2D(0.5, 1)
    result = clip_polygon(square_poly, line_start, line_end)
    
    expected_points = {
        (0, 0), (1, 0), (1, 0.5), (0.5, 1), (0, 1)
    }
    assert len(result) == 5
    assert tuple_set(result) == expected_points

def test_clip_concave_polygon():
    """Test clipping a concave polygon."""
    concave_poly = [Point2D(0,0), Point2D(2,0), Point2D(1,1), Point2D(2,2), Point2D(0,2)]
    # Vertical line at x=1.5, pointing up. "inside" is x <= 1.5
    line_start = Point2D(1.5, 0)
    line_end = Point2D(1.5, 2)
    result = clip_polygon(concave_poly, line_start, line_end)
    
    # My manual trace confirmed the algorithm correctly produces 7 vertices.
    assert len(result) == 7
    
def test_clip_empty_polygon():
    """Test clipping an empty polygon."""
    result = clip_polygon([], Point2D(0,0), Point2D(1,1))
    assert result == []

def test_clip_collinear_edge(square_poly):
    """Test clipping with a line collinear with a polygon edge."""
    # Line is the top edge of the square, directed leftwards
    line_start = Point2D(1, 1)
    line_end = Point2D(0, 1)
    result = clip_polygon(square_poly, line_start, line_end)
    # The "left" half-plane is below the line y=1.
    assert len(result) == 4
    assert set(result) == set(square_poly)
