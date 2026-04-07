# Take-Home Interview: Polynomial Evaluation over Homomorphic Encryption

## Introduction

[Homomorphic Encryption (HE)](https://en.wikipedia.org/wiki/Homomorphic_encryption) is a form of encryption that allows computation to be performed directly on ciphertexts — without ever decrypting them. This makes it possible to evaluate functions on private data while keeping that data fully encrypted. A key constraint in leveled HE schemes is **multiplicative depth**: each multiplication consumes a "level," and once all levels are exhausted, the ciphertext can no longer be used in further multiplications. This makes depth the primary resource to optimize when designing HE-friendly algorithms.

In this problem, you will optimize the evaluation of a polynomial over an encrypted input using a simplified toy model of leveled HE.

---

## Getting Started

**Requirements:** Python 3.10+, no external dependencies.

Run the evaluation harness:

```sh
python main.py
```

This will print a table of costs for polynomial evaluation at degrees 0 through 31.

---

## Primitives

The following operations are available in `ciphertext.py`. All ciphertexts begin at `level = STARTING_LEVEL = 15`.

| Operation | Description | Depth Cost | Notes |
|---|---|---|---|
| `encrypt(value)` | Encrypts a plaintext float into a `Ciphertext` | 0 | Returns a fresh ciphertext at level 15 |
| `sum_cts(addends)` | Adds a list of ciphertexts together | 0 | Output level = min of input levels |
| `pt_ct_dot_product(coeffs, cts)` | Dot product of plaintext floats against ciphertexts | 1 | Costs one level; cheaper in real HE |
| `ct_ct_dot_product(coeffs, cts)` | Dot product of ciphertexts against ciphertexts | 1 | Costs one level; significantly more expensive in real HE |

**Key insight:** Addition is free (no depth cost). Dot products — whether `pt_ct_dot_product` or `ct_ct_dot_product` — always cost one level. However, `ct_ct_dot_product` is substantially more expensive in real-world HE systems, so minimizing its use is a secondary priority.

---

## Task

Your task is to replace the naive `evaluate_ct` method in `polynomial.py` with an optimized implementation.

```python
# polynomial.py
def evaluate_ct(self, x: Ciphertext) -> Ciphertext:
    # Your implementation goes here
    ...
```

The method receives an encrypted input `x` (a `Ciphertext`) and must return a `Ciphertext` representing the evaluated polynomial — identical in behavior to `evaluate_pt`, but operating entirely on ciphertexts.

The provided reference implementation is intentionally suboptimal. You are free to use any algorithm you like.

### Optimization Objective (strict priority order)

1. **Minimize multiplicative depth** *(most important)* — depth = `x.level - result.level`, i.e., how many levels are consumed during evaluation.
2. **Minimize `ct_ct_dot_product` call count** *(second priority)* — these operations are most expensive in practice.
3. **Minimize `pt_ct_dot_product` call count** *(third priority)*.

Do not sacrifice depth to reduce operation counts. Lower depth is always better, regardless of the tradeoff.

---

## Evaluation

Running `python main.py` calls `cost(degree)` for each polynomial degree from 0 to 31 and prints the result. For each degree, the output reports:

- **depth** — multiplicative levels consumed
- **ct_ct_dot_product count** — number of ciphertext-ciphertext dot products performed
- **pt_ct_dot_product count** — number of plaintext-ciphertext dot products performed

Submissions will be evaluated against the naive baseline on these three metrics, in the strict priority order described above. A correct submission must produce the same numerical result as `evaluate_pt` for all test inputs and all degrees.

---

## Rules

- You may use AI tools and the Internet freely.
- This must be completed **individually** — do not ask other people for help or collaborate with others.
