"""
Polynomial evaluation over plaintexts and FHE ciphertexts.

Provides a ``Polynomial`` class that can evaluate a polynomial either in the
clear (for reference and testing) or homomorphically over encrypted inputs.
The homomorphic path is intentionally naive and is the target of optimization
in the take-home interview problem.
"""

from ciphertext import Ciphertext, sum_cts, pt_ct_dot_product, ct_ct_dot_product

class Polynomial:
    """A polynomial with real-valued coefficients, stored in ascending degree order.

    ``coeffs[i]`` is the coefficient of ``x**i``, so ``coeffs[0]`` is the
    constant term and ``coeffs[-1]`` is the leading coefficient.
    """

    degree: int
    coeffs: list[float]

    def __init__(self, coeffs: list[float]) -> None:
        """
        Initialize the polynomial from a coefficient list in ascending degree order.
        """
        self.degree = len(coeffs) - 1
        self.coeffs = coeffs

    def evaluate_pt(self, x: float) -> float:
        """Evaluate the polynomial at a plaintext value.
        """
        result = 0
        for i, coeff in enumerate(self.coeffs):
            result += coeff * x ** i
        return result

    def evaluate_ct(self, x: Ciphertext) -> Ciphertext:
        """Evaluate the polynomial homomorphically at an encrypted value ``x``.

        Your goal is to replace this with a more efficient algorithm.

        Optimization objective:
          1. Minimize multiplicative depth (levels consumed).
          2. Minimize ct-ct dot product calls, conditioned on depth being optimal.
          3. Minimize pt-ct dot product calls, conditioned on (1) and (2) being optimal.
        """
        def pt_ct_mul(pt: float, ct: Ciphertext) -> Ciphertext:
            return pt_ct_dot_product([pt], [ct])

        def ct_ct_mul(ct1: Ciphertext, ct2: Ciphertext) -> Ciphertext:
            return ct_ct_dot_product([ct1], [ct2])

        def power(ct: Ciphertext, d: int):
            if d < 0:
                raise ValueError(f"cannot raise ciphertext to negative power (d={d})")
            elif d == 0:
                return Ciphertext.encrypt(1)
            else:
                return ct_ct_mul(ct, power(ct, d-1))

        terms = [pt_ct_mul(coeff, power(x, i)) for i, coeff in enumerate(self.coeffs)]
        result = sum_cts(terms)

        return result
