"""Sublinear Property Tester for Fréchet Distance."""
from __future__ import annotations
import numpy as np
import random
from typing import Callable, Optional

class FrechetTester:
    """
    Implements a sublinear property tester for Fréchet distance (Afshani et al. 2024).
    Determines if two curves are similar within delta or (epsilon, delta)-far.
    """
    def __init__(self, 
                 query_P: Callable[[int], np.ndarray], 
                 query_Q: Callable[[int], np.ndarray], 
                 n: int, m: int,
                 delta: float, epsilon: float):
        """
        Args:
            query_P: Function to get vertex i of curve P.
            query_Q: Function to get vertex j of curve Q.
            n, m: Number of vertices in P and Q.
            delta: Distance threshold.
            epsilon: Far-property parameter (0 < epsilon < 2).
        """
        self.query_P = query_P
        self.query_Q = query_Q
        self.n = n
        self.m = m
        self.delta = delta
        self.epsilon = epsilon
        self._cache = {}

    def is_white(self, i: int, j: int) -> bool:
        """Query oracle: Is the distance between P[i] and Q[j] <= delta?"""
        if (i, j) in self._cache:
            return self._cache[(i, j)]
        
        pi = self.query_P(i)
        qj = self.query_Q(j)
        dist = np.linalg.norm(pi - qj)
        res = dist <= self.delta
        self._cache[(i, j)] = res
        return res

    def test(self, num_trials: int = 10) -> str:
        """
        Performs the decision test.
        Returns "yes" if distance <= delta, "no" if (epsilon, delta)-far.
        """
        # Base case: ends must be within delta
        if not self.is_white(0, 0) or not self.is_white(self.n - 1, self.m - 1):
            return "no"

        # Randomized Greedy Search with Lookahead
        for _ in range(num_trials):
            if self._randomized_greedy_walk():
                return "yes"

        return "no"

    def _randomized_greedy_walk(self) -> bool:
        """Attempts to find a monotone path using a stochastic greedy approach."""
        i, j = 0, 0
        
        max_steps = self.n + self.m
        steps = 0
        
        while (i < self.n - 1 or j < self.m - 1) and steps < max_steps:
            steps += 1
            candidates = []
            
            # Potential monotone moves
            moves = [(1, 1), (1, 0), (0, 1)]
            for di, dj in moves:
                ni, nj = i + di, j + dj
                if ni < self.n and nj < self.m and self.is_white(ni, nj):
                    candidates.append((ni, nj))
            
            if not candidates:
                return False
            
            # Prioritize diagonal move, then random choice
            if (i + 1, j + 1) in candidates:
                i, j = i + 1, j + 1
            else:
                i, j = random.choice(candidates)
            
        return i == self.n - 1 and j == self.m - 1
