"""
Evaluation harness for the take-home interview task.

Candidates implement ``Polynomial.evaluate_ct`` in ``polynomial.py``; this
module measures the multiplicative depth and dot-product counts of that
implementation across polynomial degrees 0–31.
"""

from random import random, seed

from polynomial import Polynomial
from ciphertext import encrypt
from utils import CallCounter

seed(42)

# Fixed test points used for correctness verification in cost().
_CORRECTNESS_TEST_POINTS = [0.1, 0.25, 0.618, 0.9]


def cost(degree: int) -> tuple[int, int, int]:
    """
    Evaluate a random degree-``degree`` polynomial on several test inputs and
    return the three optimization metrics, in priority order.

    Correctness is verified against ``evaluate_pt`` at a set of fixed test
    points as well as one random point before metrics are collected.

    Parameters
    ----------
    degree : int
        Degree of the randomly generated polynomial (must be >= 0).

    Returns
    -------
    depth_count : int
        Multiplicative depth consumed by the evaluation
        (``ct.level - result.level``; each multiplication decrements level by 1).
        This is the most important metric to minimize.
    ct_ct_dot_product_count : int
        Number of ciphertext-ciphertext dot product operations performed.
    pt_ct_dot_product_count : int
        Number of plaintext-ciphertext dot product operations performed.

    Raises
    ------
    AssertionError
        If ``degree`` is negative, or if the encrypted result differs from the
        plaintext result by more than 1e-6 at any test point (correctness check).
    """
    assert degree >= 0, "degree must be non-negative"

    coeffs = [random() for _ in range(degree + 1)]
    p = Polynomial(coeffs)

    # Verify correctness at fixed test points (no metrics collected here).
    for x in _CORRECTNESS_TEST_POINTS:
        ct = encrypt(x)
        expected = p.evaluate_pt(x)
        actual = p.evaluate_ct(ct).decrypt()
        assert abs(actual - expected) < 1e-6, (
            f"Correctness failure at x={x}, degree={degree}: "
            f"expected {expected}, got {actual}"
        )

    # Collect metrics on one random evaluation point.
    call_counter = CallCounter()
    with call_counter:
        x = random()
        ct = encrypt(x)
        expected_result = p.evaluate_pt(x)
        actual_result = p.evaluate_ct(ct)
        assert abs(actual_result.decrypt() - expected_result) < 1e-6, (
            f"Correctness failure at random x={x}, degree={degree}: "
            f"expected {expected_result}, got {actual_result.decrypt()}"
        )

    depth_count = ct.level - actual_result.level
    ct_ct_dot_product_count = call_counter.counts.get("ct_ct_dot_product", 0)
    pt_ct_dot_product_count = call_counter.counts.get("pt_ct_dot_product", 0)

    return (depth_count, ct_ct_dot_product_count, pt_ct_dot_product_count)


# Run cost() for every polynomial degree from 0 to 31 and print the three
# optimization metrics in a table so candidates can compare their
# implementation's depth and dot-product usage at a glance.
if __name__ == "__main__":
    col_w = [8, 7, 12, 12]
    header = (
        f"{'degree':>{col_w[0]}}"
        f"{'depth':>{col_w[1]}}"
        f"{'ct-ct ops':>{col_w[2]}}"
        f"{'pt-ct ops':>{col_w[3]}}"
    )
    separator = "-" * len(header)

    print(header)
    print(separator)

    for degree in range(32):
        depth, ct_ct, pt_ct = cost(degree)
        print(
            f"{degree:>{col_w[0]}}" +
            f"{depth:>{col_w[1]}}" +
            f"{ct_ct:>{col_w[2]}}" +
            f"{pt_ct:>{col_w[3]}}"
        )
