"""Multivariate polynomial representation and arithmetic."""
from __future__ import annotations
from typing import Dict, Tuple, List, Optional
import math

class MultivariatePolynomial:
    """
    Represents a multivariate polynomial as a mapping from exponent tuples to coefficients.
    e.g., f(x, y) = 3x^2y - 5y + 2 is {(2, 1): 3.0, (0, 1): -5.0, (0, 0): 2.0}.
    """
    def __init__(self, terms: Dict[Tuple[int, ...], float], num_vars: Optional[int] = None):
        # Filter out zero coefficients
        self.terms = {tuple(exp): float(coeff) for exp, coeff in terms.items() if abs(coeff) > 1e-12}
        if num_vars is None:
            self.num_vars = max(len(exp) for exp in self.terms.keys()) if self.terms else 0
        else:
            self.num_vars = num_vars
            
        # Standardize exponent tuple length
        new_terms = {}
        for exp, coeff in self.terms.items():
            full_exp = list(exp) + [0] * (self.num_vars - len(exp))
            new_terms[tuple(full_exp)] = coeff
        self.terms = new_terms

    def __add__(self, other: MultivariatePolynomial) -> MultivariatePolynomial:
        n = max(self.num_vars, other.num_vars)
        new_terms = self.terms.copy()
        for exp, coeff in other.terms.items():
            full_exp = list(exp) + [0] * (n - len(exp))
            key = tuple(full_exp)
            new_terms[key] = new_terms.get(key, 0.0) + coeff
        return MultivariatePolynomial(new_terms, n)

    def __sub__(self, other: MultivariatePolynomial) -> MultivariatePolynomial:
        n = max(self.num_vars, other.num_vars)
        new_terms = self.terms.copy()
        for exp, coeff in other.terms.items():
            full_exp = list(exp) + [0] * (n - len(exp))
            key = tuple(full_exp)
            new_terms[key] = new_terms.get(key, 0.0) - coeff
        return MultivariatePolynomial(new_terms, n)

    def __mul__(self, other: MultivariatePolynomial) -> MultivariatePolynomial:
        n = max(self.num_vars, other.num_vars)
        new_terms = {}
        for exp1, coeff1 in self.terms.items():
            for exp2, coeff2 in other.terms.items():
                new_exp = tuple(exp1[i] + exp2[i] for i in range(n))
                new_terms[new_exp] = new_terms.get(new_exp, 0.0) + coeff1 * coeff2
        return MultivariatePolynomial(new_terms, n)

    def leading_term(self, order: str = 'lex') -> Tuple[Tuple[int, ...], float]:
        """Returns (exponent, coeff) of the leading term according to order."""
        if not self.terms:
            return (tuple([0]*self.num_vars), 0.0)
            
        if order == 'lex':
            # Lexicographical order
            exp = max(self.terms.keys())
        elif order == 'grevlex':
            # Graded Reverse Lexicographical order
            def grevlex_key(e):
                total_deg = sum(e)
                # Reverse components for reverse lex
                return (total_deg, tuple(reversed(e)))
            exp = max(self.terms.keys(), key=grevlex_key)
        else:
            raise ValueError(f"Unsupported ordering: {order}")
            
        return exp, self.terms[exp]

    def evaluate(self, point: List[float]) -> float:
        """Evaluates the polynomial at a given point."""
        res = 0.0
        for exp, coeff in self.terms.items():
            term_val = coeff
            for i in range(min(len(exp), len(point))):
                term_val *= (point[i] ** exp[i])
            res += term_val
        return res

    def __repr__(self) -> str:
        if not self.terms: return "0"
        parts = []
        # Sort terms by degree then lex for readable representation
        sorted_exps = sorted(self.terms.keys(), key=lambda e: (sum(e), e), reverse=True)
        for exp in sorted_exps:
            coeff = self.terms[exp]
            s_coeff = f"{coeff:+} " if abs(coeff - 1.0) > 1e-9 else "+ "
            if abs(coeff + 1.0) < 1e-9: s_coeff = "- "
            
            vars_part = "".join([f"x{i}^{e}" if e > 1 else (f"x{i}" if e == 1 else "") for i, e in enumerate(exp)])
            if not vars_part: vars_part = str(abs(coeff))
            parts.append(f"{s_coeff}{vars_part}")
        return " ".join(parts).strip("+ ")
