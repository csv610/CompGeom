import math
from typing import List, Optional


class HammersleyPointsGenerator:
    """
    A class to generate Hammersley points in N-dimensional space.
    The Hammersley sequence is a low-discrepancy quasi-random sequence
    that generalizes the van der Corput sequence to higher dimensions.
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

    @staticmethod
    def _reverse_bits(n: int, bits: int) -> int:
        result = 0
        for i in range(bits):
            result = (result << 1) | (n & 1)
            n >>= 1
        return result

    def _hammersley_sequence(self, index: int) -> List[float]:
        result = []
        for d in range(self.dimensions):
            if d == 0:
                result.append(index / (2**32))
            else:
                prime = self._primes[d - 1] if d - 1 < len(self._primes) else 2
                val = 0
                base = prime
                exp = 1
                n = index
                while n > 0:
                    val += (n % base) * (1.0 / (base**exp))
                    n //= base
                    exp += 1
                result.append(val)
        return result

    @property
    def _primes(self) -> List[int]:
        return [2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37, 41, 43, 47]

    def get_point(self, index: int) -> List[float]:
        """Generates the n-th point in the sequence, scaled to the bounding box."""
        hammersley_point = self._hammersley_sequence(index)
        return [
            self.box_min[d] + hammersley_point[d] * (self.box_max[d] - self.box_min[d]) for d in range(self.dimensions)
        ]

    def generate(self, n_points: int, start_index: int = 0) -> List[List[float]]:
        """Generates a list of n points starting from start_index."""
        return [self.get_point(i) for i in range(start_index, start_index + n_points)]
