# Halton Points (Low-Discrepancy Sequence)

## 1. Overview
Halton sequences are a type of low-discrepancy sequence used to generate points in a $d$-dimensional space. Unlike pseudo-random numbers, which can clump together, low-discrepancy sequences are designed to be "more uniform than random," ensuring that every part of the domain is sampled evenly. Halton points are a generalization of the 1D **van der Corput sequence** to higher dimensions using different prime numbers as bases.

## 2. Definitions
*   **Low-Discrepancy Sequence**: A sequence of points where the number of points in any sub-region is proportional to the region's volume.
*   **Quasi-Monte Carlo (QMC)**: Integration and simulation methods that use low-discrepancy sequences instead of random numbers.
*   **Van der Corput Sequence**: A 1D sequence in a base $b$ formed by reversing the digits of the base-$b$ representation of integers.
*   **Discrepancy**: A mathematical measure of how "non-uniform" a set of points is.

## 3. Theory
The Halton sequence in $d$ dimensions is constructed by using the first $d$ prime numbers as bases ($p_1, p_2, \dots, p_d$). The $i$-th point in the sequence is:
$$x_i = (\phi_{p_1}(i), \phi_{p_2}(i), \dots, \phi_{p_d}(i))$$
where $\phi_b(i)$ is the **radical inverse function** in base $b$.

To compute $\phi_b(i)$:
1.  Write $i$ in base $b$: $i = \sum a_k b^k$.
2.  Reverse the digits and place them after a decimal point: $\phi_b(i) = \sum a_k b^{-(k+1)}$.

Because the prime bases are co-prime, the coordinates in different dimensions are effectively "de-correlated," filling the $d$-dimensional unit hypercube uniformly.

## 4. Pseudo code
```python
function HaltonSequence(num_points, dimensions):
    primes = GetFirstPrimes(dimensions)
    points = []
    
    for i in range(1, num_points + 1):
        point = []
        for d in range(dimensions):
            point.append(RadicalInverse(i, primes[d]))
        points.append(point)
        
    return points

function RadicalInverse(n, base):
    val = 0
    inv_base = 1.0 / base
    f = inv_base
    while n > 0:
        val += (n % base) * f
        n //= base
        f *= inv_base
    return val
```

## 5. Parameters Selections
*   **Prime Bases**: Must use unique prime numbers for each dimension. Using non-primes or identical bases will lead to strong correlations (linear patterns).
*   **Burn-in (Leaping)**: For higher dimensions, the first few hundred points can show patterns. "Scrambled Halton" or skipping the initial points can improve uniformity.

## 6. Complexity
*   **Time Complexity**: $O(N \cdot D \cdot \log_b N)$ to generate $N$ points in $D$ dimensions. Since $b$ is small, this is very fast.
*   **Space Complexity**: $O(D)$ to store the current point (or $O(N \cdot D)$ to store the full sequence).

## 7. Usages
*   **Quasi-Monte Carlo Integration**: Estimating high-dimensional integrals with faster convergence ($O(1/N)$) than standard Monte Carlo ($O(1/\sqrt{N})$).
*   **Computer Graphics**: Sampling light sources and pixels for ray tracing and path tracing.
*   **Physics Simulation**: Initializing particles in a way that minimizes clumping.
*   **Global Optimization**: Sampling the search space for black-box optimization algorithms.
*   **Financial Modeling**: Pricing complex derivatives where high-dimensional integrals are involved.

## 8. Testing methods and Edge cases
*   **Range Check**: All coordinates must be in the interval $[0, 1)$.
*   **Uniformity**: Test using the "Chi-Squared" test or by calculating the actual discrepancy of the set.
*   **Dimension Correlation**: Plot 2D projections of high-dimensional sequences (e.g., dim 10 vs dim 11) to check for "ghosting" patterns.
*   **Large $N$**: Ensure the radical inverse function doesn't lose precision for very large indices.
*   **Base Selection**: Verify that using the same base for two dimensions results in points lying on a single line.

## 9. References
*   Halton, J. H. (1960). "On the efficiency of certain quasi-random sequences of points in evaluating multi-dimensional integrals". Numerische Mathematik.
*   Niederreiter, H. (1992). "Random Number Generation and Quasi-Monte Carlo Methods". SIAM.
*   Van der Corput, J. G. (1935). "Verteilungsfunktionen". Proc. Akad. Wet. Amsterdam.
*   Wikipedia: [Halton sequence](https://en.wikipedia.org/wiki/Halton_sequence)
