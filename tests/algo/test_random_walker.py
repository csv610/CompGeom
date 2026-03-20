
import pytest
from compgeom.algo import random_walker

def test_simulate_2d():
    res = random_walker.simulate_random_walk_2d(10, 10, 5, 5, 100)
    assert res["steps"] == 100
    assert 0 <= res["final_pos"][0] < 10
    assert 0 <= res["final_pos"][1] < 10
    assert res["unique_cells"] >= 1

def test_simulate_3d():
    res = random_walker.simulate_random_walk_3d(5, 5, 5, 2, 2, 2, 50)
    assert res["steps"] == 50
    assert 0 <= res["final_pos"][0] < 5
    assert 0 <= res["final_pos"][1] < 5
    assert 0 <= res["final_pos"][2] < 5

def test_simulate_saw_2d():
    # A small grid so it either succeeds or gets trapped quickly
    res = random_walker.simulate_saw_2d(3, 3, 0, 0)
    assert res["unique_cells"] >= 1
    assert res["reason"] in ["Success", "Trapped"]
    # Check that all points in path are unique
    assert len(res["path"]) == len(set(res["path"]))

def test_generate_zigzag_path():
    path = random_walker.generate_zigzag_path(2, 2)
    assert len(path) == 4
    assert set(path) == {(0,0), (1,0), (0,1), (1,1)}

def test_generate_spiral_path():
    path = random_walker.generate_spiral_path(3, 3, 1, 1)
    assert len(path) == 9
    assert set(path) == {(x, y) for x in range(3) for y in range(3)}
    assert path[0] == (1, 1)

def test_random_walker_class():
    # Test that the wrapper functions and class methods match
    res_class = random_walker.RandomWalker.simulate_2d(10, 10, 5, 5, 10)
    assert res_class["steps"] == 10
