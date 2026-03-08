# `dynamic_delaunay.py`

Purpose: demonstration script for incremental Delaunay insertion.

Algorithm:
- creates random points
- inserts them one by one into `triangulation.DynamicDelaunay`
- local edge legalization restores the Delaunay property after each insertion

Input: none from standard input; points are generated internally.

Output: final triangle ids after incremental insertion.

Assumptions: intended as a demo, not a robust batch loader.
