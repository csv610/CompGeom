import random
from typing import List, Optional


class LatinHypercubeGenerator:
    """
    A class to generate Latin Hypercube Sample points in N-dimensional space.
    LHS ensures that each sample is the only one in each hyperplane
    along each coordinate axis, providing better coverage than pure random.
    """

    def __init__(self, dimensions: int = 2, box_min=None, box_max=None, criterion: str = "center"):
        """
        Initialize the generator.

        :param dimensions: Number of dimensions (default 2).
        :param box_min: List of minimum values for each dimension.
        :param box_max: List of maximum values for each dimension.
        :param criterion: Sampling criterion - "center", "maximin", or "correlation".
        """
        self.dimensions = dimensions
        self.criterion = criterion

        self.box_min = box_min if box_min is not None else [0.0] * dimensions
        self.box_max = box_max if box_max is not None else [1.0] * dimensions

        if len(self.box_min) != dimensions or len(self.box_max) != dimensions:
            raise ValueError("box_min and box_max must match the number of dimensions.")

    def generate(self, n_points: int, seed: Optional[int] = None) -> List[List[float]]:
        """
        Generate n_points using Latin Hypercube Sampling.

        :param n_points: Number of points to generate.
        :param seed: Random seed for reproducibility.
        :return: List of points in d-dimensional space.
        """
        if seed is not None:
            random.seed(seed)

        points: List[List[float]] = []

        for dim in range(self.dimensions):
            intervals = [i / n_points for i in range(n_points)]

            if self.criterion == "center":
                samples = [i + 0.5 / n_points for i in intervals]
            else:
                samples = [random.uniform(intervals[i], intervals[i + 1]) for i in range(n_points)]

            random.shuffle(samples)

            while len(points) < len(samples):
                points.append([])
            for i in range(n_points):
                scaled = self.box_min[dim] + samples[i] * (self.box_max[dim] - self.box_min[dim])
                points[i].append(scaled)

        return points

    def generate_center(self, n_points: int) -> List[List[float]]:
        """Generate centered LHS (more uniform)."""
        old_criterion = self.criterion
        self.criterion = "center"
        result = self.generate(n_points)
        self.criterion = old_criterion
        return result

    def generate_maximin(self, n_points: int, seed: Optional[int] = None) -> List[List[float]]:
        """Generate LHS optimized for maximum minimum distance."""
        if seed is not None:
            random.seed(seed)

        best_points = self.generate(n_points)
        best_min_dist = self._min_distance(best_points)

        for _ in range(100):
            candidate = self.generate(n_points)
            min_dist = self._min_distance(candidate)
            if min_dist > best_min_dist:
                best_points = candidate
                best_min_dist = min_dist

        return best_points

    def _min_distance(self, points: List[List[float]]) -> float:
        """Compute minimum pairwise distance."""
        min_dist = float("inf")
        n = len(points)
        for i in range(n):
            for j in range(i + 1, n):
                dist = sum((points[i][d] - points[j][d]) ** 2 for d in range(self.dimensions)) ** 0.5
                if dist < min_dist:
                    min_dist = dist
        return min_dist
