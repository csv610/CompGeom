"""Gröbner Basis computation using Buchberger's Algorithm."""
from __future__ import annotations
import numpy as np
from typing import List, Tuple, Optional

from compgeom.algebraic.polynomial import MultivariatePolynomial

class GrobnerBasis:
    """
    Computes and manages a Gröbner basis for a polynomial ideal.
    """
    @staticmethod
    def solve(F: List[MultivariatePolynomial], order: str = 'lex') -> List[MultivariatePolynomial]:
        """
        Computes a Gröbner basis for the set of polynomials F using Buchberger's algorithm.
        """
        G = list(F)
        pairs = [(G[i], G[j]) for i in range(len(G)) for j in range(i + 1, len(G))]
        
        while pairs:
            f, g = pairs.pop(0)
            s = GrobnerBasis.s_polynomial(f, g, order)
            r = GrobnerBasis.reduce(s, G, order)
            
            if len(r.terms) > 0:
                # New basis element found
                for existing in G:
                    pairs.append((existing, r))
                G.append(r)
                
        return GrobnerBasis.minimize_and_reduce(G, order)

    @staticmethod
    def s_polynomial(f: MultivariatePolynomial, g: MultivariatePolynomial, order: str = 'lex') -> MultivariatePolynomial:
        """Computes the S-polynomial of f and g."""
        exp_f, coeff_f = f.leading_term(order)
        exp_g, coeff_g = g.leading_term(order)
        
        # Least Common Multiple of leading monomials
        lcm_exp = tuple(max(exp_f[i], exp_g[i]) for i in range(f.num_vars))
        
        # multiplier_f = lcm / LT(f)
        mult_f_exp = tuple(lcm_exp[i] - exp_f[i] for i in range(f.num_vars))
        mult_f = MultivariatePolynomial({mult_f_exp: 1.0 / coeff_f}, f.num_vars)
        
        # multiplier_g = lcm / LT(g)
        mult_g_exp = tuple(lcm_exp[i] - exp_g[i] for i in range(f.num_vars))
        mult_g = MultivariatePolynomial({mult_g_exp: 1.0 / coeff_g}, g.num_vars)
        
        return (mult_f * f) - (mult_g * g)

    @staticmethod
    def reduce(f: MultivariatePolynomial, G: List[MultivariatePolynomial], order: str = 'lex') -> MultivariatePolynomial:
        """
        Reduces polynomial f by the set G (multivariate long division).
        Returns the remainder r such that no term in r is divisible by any LT(g) in G.
        """
        r = MultivariatePolynomial({}, f.num_vars)
        p = f
        
        while len(p.terms) > 0:
            found_divisor = False
            exp_p, coeff_p = p.leading_term(order)
            
            for g in G:
                exp_g, coeff_g = g.leading_term(order)
                # Check divisibility: all(exp_p[i] >= exp_g[i])
                if all(exp_p[i] >= exp_g[i] for i in range(p.num_vars)):
                    # p = p - (LT(p)/LT(g)) * g
                    quotient_exp = tuple(exp_p[i] - exp_g[i] for i in range(p.num_vars))
                    quotient_coeff = coeff_p / coeff_g
                    quotient = MultivariatePolynomial({quotient_exp: quotient_coeff}, p.num_vars)
                    p = p - (quotient * g)
                    found_divisor = True
                    break
            
            if not found_divisor:
                # Add LT(p) to remainder and remove it from p
                lt_p = MultivariatePolynomial({exp_p: coeff_p}, p.num_vars)
                r = r + lt_p
                p = p - lt_p
                
        return r

    @staticmethod
    def minimize_and_reduce(G: List[MultivariatePolynomial], order: str = 'lex') -> List[MultivariatePolynomial]:
        """Cleans up the basis by removing redundant elements and reducing them."""
        # 1. Minimize: remove g such that LT(g) is divisible by LT(g') for g' in G
        minimal = []
        for i, g in enumerate(G):
            exp_g, _ = g.leading_term(order)
            keep = True
            for j, g_prime in enumerate(G):
                if i == j: continue
                exp_gp, _ = g_prime.leading_term(order)
                if all(exp_g[k] >= exp_gp[k] for k in range(g.num_vars)):
                    # If same leading monomial, keep the one with smaller index to avoid removing both
                    if exp_g == exp_gp and i > j:
                        keep = False
                        break
                    elif exp_g != exp_gp:
                        keep = False
                        break
            if keep:
                # Normalize leading coefficient to 1
                _, lc = g.leading_term(order)
                normalized = MultivariatePolynomial({e: c/lc for e, c in g.terms.items()}, g.num_vars)
                minimal.append(normalized)
                
        # 2. Fully reduce
        reduced = []
        for i in range(len(minimal)):
            g = minimal[i]
            others = minimal[:i] + minimal[i+1:]
            r = GrobnerBasis.reduce(g, others, order)
            reduced.append(r)
            
        return reduced
