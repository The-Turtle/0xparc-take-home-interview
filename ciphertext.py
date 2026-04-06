"""
Simplified toy model of leveled Fully Homomorphic Encryption (FHE).

Values and levels are stored in plaintext solely to simulate the behavior of a
leveled HE scheme: each ciphertext carries a multiplicative-depth budget
('level') that decrements by 1 per dot-product (multiplication) and is
unaffected by addition.
"""
from __future__ import annotations
from collections.abc import Sequence

from utils import count_calls

STARTING_LEVEL = 15

class Ciphertext:
    """
    Simulated FHE ciphertext holding a plaintext value and a level.

    The level represents the remaining multiplicative-depth budget; a freshly
    encrypted ciphertext starts at STARTING_LEVEL and loses 1 level per
    dot-product operation.
    """
    value: float
    level: int

    def __init__(self, value: float, level: int | None = None):
        self.value = value
        if level is None:
            self.level = STARTING_LEVEL
        else:
            self.level = level

    @classmethod
    def encrypt(cls, value: float) -> Ciphertext:
        """Encrypt a plaintext float, returning a fresh Ciphertext at STARTING_LEVEL."""
        return Ciphertext(value=value)

    def decrypt(self) -> float:
        """Decrypt the ciphertext, returning the underlying plaintext float."""
        return self.value


def encrypt(value: float) -> Ciphertext:
    return Ciphertext.encrypt(value)


def sum_cts(addends: Sequence[float | Ciphertext]) -> Ciphertext:
    """
    Sum a sequence of plaintexts and/or ciphertexts without consuming level.

    The output level is the minimum level among any Ciphertext inputs.
    """
    result = 0
    for addend in addends:
        value = addend.value if isinstance(addend, Ciphertext) else addend
        result += value

    all_levels = [addend.level for addend in addends if isinstance(addend, Ciphertext)]
    output_level = None if len(all_levels) == 0 else min(all_levels)

    return Ciphertext(result, level = output_level)


def _dot_product(coeffs: Sequence[float | Ciphertext], cts: Sequence[float | Ciphertext]) -> Ciphertext:
    """
    Compute the dot product of two equal-length sequences, consuming 1 level.

    The output level is min(levels of all Ciphertext inputs) - 1, reflecting
    the one unit of multiplicative depth consumed by this operation.
    """
    assert len(coeffs) == len(cts), f"length mismatch: {len(coeffs)} != {len(cts)}"

    result = 0
    for coeff, ct in zip(coeffs, cts):
        coeff_value = coeff.value if isinstance(coeff, Ciphertext) else coeff
        ct_value = ct.value if isinstance(ct, Ciphertext) else ct
        result += coeff_value * ct_value

    all_levels = [ct.level for ct in list(coeffs) + list(cts) if isinstance(ct, Ciphertext)]
    output_level = None if len(all_levels) == 0 else min(all_levels) - 1

    return Ciphertext(result, level = output_level)


@count_calls
def pt_ct_dot_product(coeffs: list[float], cts: list[float | Ciphertext]) -> Ciphertext:
    """
    Dot product of plaintext coefficients with ciphertext (or plaintext) inputs.
    Consumes 1 level.
    """
    return _dot_product(coeffs, cts)


@count_calls
def ct_ct_dot_product(coeffs: list[float | Ciphertext], cts: list[float | Ciphertext]) -> Ciphertext:
    """
    Dot product where both coefficients and inputs may be ciphertexts.
    Consumes 1 level.
    """
    return _dot_product(coeffs, cts)
