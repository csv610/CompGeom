import math
from typing import List, Optional


class SobolPointsGenerator:
    """
    A class to generate Sobol points in N-dimensional space.
    The Sobol sequence is a low-discrepancy quasi-random sequence
    using base-2 for maximum uniformity.
    """

    def __init__(self, dimensions: int = 2, box_min=None, box_max=None):
        """
        Initialize the generator.

        :param dimensions: Number of dimensions (default 2).
        :param box_min: List of minimum values for each dimension.
        :param box_max: List of maximum values for each dimension.
        """
        self.dimensions = dimensions

        self.box_min = box_min if box_min is not None else [0.0] * dimensions
        self.box_max = box_max if box_max is not None else [1.0] * dimensions

        if len(self.box_min) != dimensions or len(self.box_max) != dimensions:
            raise ValueError("box_min and box_max must match the number of dimensions.")

        self._direction_numbers = self._generate_direction_numbers()

    def _generate_direction_numbers(self) -> List[List[int]]:
        max_bits = 31
        direction_numbers = []

        primitives = [
            (1, 1, 3),
            (1, 1, 7),
            (2, 1, 15),
            (1, 3, 1),
            (1, 1, 9),
            (4, 1, 5),
            (2, 1, 13),
            (1, 1, 25),
            (2, 3, 1),
            (1, 3, 7),
        ]

        for dim in range(1, self.dimensions + 1):
            if dim <= len(primitives):
                v = [0] * (max_bits + 1)
                poly, init, bit = primitives[dim - 1]
                for i in range(1, bit + 1):
                    if i <= 1:
                        v[i] = init
                    else:
                        v[i] = (v[i - poly] ^ (v[i - poly] >> 1)) << 1
                        if i > 1:
                            for j in range(poly, i):
                                if (bit >> (j - poly)) & 1:
                                    v[i] ^= v[j]
                direction_numbers.append(v[1 : max_bits + 1])
            else:
                v = [0] * (max_bits + 1)
                for i in range(2, max_bits + 1):
                    v[i] = 1 << (i - 1)
                direction_numbers.append(v[1 : max_bits + 1])

        return direction_numbers

    def _sobol_sequence(self, index: int) -> List[float]:
        if index == 0:
            return [0.0] * self.dimensions

        result = []
        for d in range(self.dimensions):
            val = 0
            i = index
            bit = 1
            while i > 0:
                if i & 1:
                    val ^= self._direction_numbers[d][bit - 1]
                i >>= 1
                bit += 1
            result.append(val / (1 << 30))
        return result

    def get_point(self, index: int) -> List[float]:
        """Generates the n-th point in the sequence, scaled to the bounding box."""
        sobol_point = self._sobol_sequence(index)
        return [self.box_min[d] + sobol_point[d] * (self.box_max[d] - self.box_min[d]) for d in range(self.dimensions)]

    def generate(self, n_points: int, start_index: int = 1) -> List[List[float]]:
        """Generates a list of n points starting from start_index."""
        return [self.get_point(i) for i in range(start_index, start_index + n_points)]
