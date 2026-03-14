import sys

class HaltonPointsGenerator:
    """
    A class to generate Halton points in N-dimensional space.
    The Halton sequence is a low-discrepancy sequence used to generate 
    quasi-random points that are more uniformly distributed than random points.
    """
    
    def __init__(self, dimensions=2, box_min=None, box_max=None, bases=None):
        """
        Initialize the generator with dimensions and bounding box.
        
        :param dimensions: Number of dimensions (default 2).
        :param box_min: List of minimum values for each dimension.
        :param box_max: List of maximum values for each dimension.
        :param bases: List of prime bases for the Halton sequence.
        """
        self.dimensions = dimensions
        
        # Default prime bases if none provided
        if bases is None:
            # A small list of primes for common dimensions
            primes = [2, 3, 5, 7, 11, 13, 17, 19, 23, 29]
            if dimensions > len(primes):
                raise ValueError(f"Default bases only support up to {len(primes)} dimensions.")
            self.bases = primes[:dimensions]
        else:
            if len(bases) < dimensions:
                raise ValueError("Number of bases must match or exceed dimensions.")
            self.bases = bases
            
        # Default box [0, 1]^N if none provided
        self.box_min = box_min if box_min is not None else [0.0] * dimensions
        self.box_max = box_max if box_max is not None else [1.0] * dimensions
        
        if len(self.box_min) != dimensions or len(self.box_max) != dimensions:
            raise ValueError("box_min and box_max must match the number of dimensions.")

    @staticmethod
    def _halton_sequence(index, base):
        """Computes the i-th element of the Halton sequence for a given base."""
        result = 0
        f = 1
        i = index
        while i > 0:
            f = f / base
            result = result + f * (i % base)
            i = i // base
        return result

    def get_point(self, index):
        """Generates the n-th point in the sequence, scaled to the bounding box."""
        point = []
        for d in range(self.dimensions):
            h = self._halton_sequence(index, self.bases[d])
            # Scale: min + h * (max - min)
            scaled = self.box_min[d] + h * (self.box_max[d] - self.box_min[d])
            point.append(scaled)
        return point

    def generate(self, n_points, start_index=1):
        """Generates a list of n points starting from start_index."""
        return [self.get_point(i) for i in range(start_index, start_index + n_points)]

