import random
import sys

class RandomPointsGenerator:
    """
    A class to generate uniformly distributed random points in N-dimensional space
    within a specified bounding box.
    """
    
    def __init__(self, dimensions=2, box_min=None, box_max=None, seed=None):
        """
        Initialize the generator with dimensions and bounding box.
        
        :param dimensions: Number of dimensions (default 2).
        :param box_min: List of minimum values for each dimension.
        :param box_max: List of maximum values for each dimension.
        :param seed: Optional seed for the random number generator.
        """
        self.dimensions = dimensions
        self.box_min = box_min if box_min is not None else [0.0] * dimensions
        self.box_max = box_max if box_max is not None else [1.0] * dimensions
        
        if len(self.box_min) != dimensions or len(self.box_max) != dimensions:
            raise ValueError("box_min and box_max must match the number of dimensions.")
        
        if seed is not None:
            random.seed(seed)

    def generate(self, n_points):
        """Generates a list of n random points within the bounding box."""
        points = []
        for _ in range(n_points):
            point = [
                random.uniform(self.box_min[d], self.box_max[d]) 
                for d in range(self.dimensions)
            ]
            points.append(point)
        return points
