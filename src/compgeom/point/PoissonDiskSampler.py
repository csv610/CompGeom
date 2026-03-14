import random
import math
import itertools

class PoissonDiskSampler:
    """
    A class to generate points in N-dimensional space using Poisson Disk Sampling.
    The algorithm ensures that no two points are closer than a minimum distance 'r'.
    Uses Bridson's algorithm for O(N) performance.
    """
    
    def __init__(self, dimensions=2, box_min=None, box_max=None, r=0.1, k=30, seed=None):
        """
        Initialize the sampler.
        
        :param dimensions: Number of dimensions (default 2).
        :param box_min: List of minimum values for each dimension.
        :param box_max: List of maximum values for each dimension.
        :param r: Minimum distance between points.
        :param k: Number of candidates to try before rejecting a point (default 30).
        :param seed: Optional seed for the random number generator.
        """
        self.dimensions = dimensions
        self.box_min = box_min if box_min is not None else [0.0] * dimensions
        self.box_max = box_max if box_max is not None else [1.0] * dimensions
        self.r = r
        self.k = k
        
        if len(self.box_min) != dimensions or len(self.box_max) != dimensions:
            raise ValueError("box_min and box_max must match the number of dimensions.")
        
        if seed is not None:
            random.seed(seed)

    def _get_distance(self, p1, p2):
        """Calculates Euclidean distance between two points."""
        return math.sqrt(sum((p1[i] - p2[i])**2 for i in range(self.dimensions)))

    def generate(self, n_points=None):
        """
        Generates points using Poisson Disk Sampling.
        
        :param n_points: If specified, stops generating after reaching this many points.
                         Otherwise, fills the space according to 'r'.
        :return: A list of points within the bounding box.
        """
        # Grid cell size ensures at most one point per cell
        cell_size = self.r / math.sqrt(self.dimensions)
        
        # Grid dimensions
        grid_dims = [
            int(math.ceil((self.box_max[i] - self.box_min[i]) / cell_size))
            for i in range(self.dimensions)
        ]
        
        # Background grid to accelerate proximity checks (maps grid coordinates to point index)
        grid = {}
        
        def get_grid_coords(p):
            return tuple(int((p[i] - self.box_min[i]) / cell_size) for i in range(self.dimensions))

        points = []
        active_list = []
        
        # Start with an initial random point
        start_point = [
            random.uniform(self.box_min[i], self.box_max[i])
            for i in range(self.dimensions)
        ]
        points.append(start_point)
        active_list.append(0)
        grid[get_grid_coords(start_point)] = 0
        
        while active_list:
            if n_points is not None and len(points) >= n_points:
                break
                
            # Pick a random active point
            idx = random.randint(0, len(active_list) - 1)
            p = points[active_list[idx]]
            
            found = False
            for _ in range(self.k):
                # Generate a candidate point in the spherical shell [r, 2r]
                if self.dimensions == 2:
                    angle = 2 * math.pi * random.random()
                    dist = random.uniform(self.r, 2 * self.r)
                    new_p = [
                        p[0] + dist * math.cos(angle),
                        p[1] + dist * math.sin(angle)
                    ]
                else:
                    # N-dimensional random point in shell
                    direction = [random.gauss(0, 1) for _ in range(self.dimensions)]
                    norm = math.sqrt(sum(x*x for x in direction))
                    direction = [x/norm for x in direction]
                    dist = random.uniform(self.r, 2 * self.r)
                    new_p = [p[i] + direction[i] * dist for i in range(self.dimensions)]
                
                # Check if candidate is within the bounding box
                in_box = all(self.box_min[i] <= new_p[i] <= self.box_max[i] for i in range(self.dimensions))
                if not in_box:
                    continue
                
                # Check if candidate is too close to existing points
                coords = get_grid_coords(new_p)
                too_close = False
                
                # Check adjacent cells (within 2 cells in each direction is sufficient)
                ranges = [
                    range(max(0, coords[i] - 2), min(grid_dims[i], coords[i] + 3)) 
                    for i in range(self.dimensions)
                ]
                
                for neighbor_coords in itertools.product(*ranges):
                    if neighbor_coords in grid:
                        if self._get_distance(new_p, points[grid[neighbor_coords]]) < self.r:
                            too_close = True
                            break
                if too_close:
                    continue
                
                # Candidate is valid
                points.append(new_p)
                active_list.append(len(points) - 1)
                grid[coords] = len(points) - 1
                found = True
                break
            
            if not found:
                active_list.pop(idx)
                
        return points[:n_points] if n_points is not None else points
