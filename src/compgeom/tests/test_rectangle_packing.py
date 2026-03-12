from compgeom.algo.rectangle_packing import RectanglePacker, PackedRect

def test_rectangle_packer_empty():
    w, h, rects = RectanglePacker.pack([])
    assert w == 0
    assert h == 0
    assert rects == []

def test_rectangle_packer_pack_rectangle():
    dimensions = [(10, 20), (20, 10), (10, 10)]
    w, h, rects = RectanglePacker.pack(dimensions, target_shape="rectangle")
    
    assert w > 0
    assert h > 0
    assert len(rects) == 3
    
    # Check if they overlap or exceed bounds
    for r in rects:
        assert r.x >= 0
        assert r.y >= 0
        assert r.x + r.width <= w
        assert r.y + r.height <= h

def test_rectangle_packer_pack_square():
    dimensions = [(10, 20), (20, 10), (10, 10), (15, 15)]
    w, h, rects = RectanglePacker.pack(dimensions, target_shape="square")
    
    assert w > 0
    assert h > 0
    assert len(rects) == 4
    
    for r in rects:
        assert r.x >= 0
        assert r.y >= 0
        assert r.x + r.width <= w
        assert r.y + r.height <= h

def test_rectangle_packer_visualize():
    placements = [
        PackedRect(0, 0, 10, 20, 0),
        PackedRect(10, 0, 20, 10, 1)
    ]
    svg = RectanglePacker.visualize(30, 20, placements)
    assert "<svg" in svg
    assert "</svg>" in svg
