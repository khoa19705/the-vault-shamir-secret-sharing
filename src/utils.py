import json
import os

# ============================================
# GLOBAL PRIME NUMBER
# Finite field for Shamir Secret Sharing
# ============================================

PRIME = 2**257 - 93

# ============================================
# Polynomial Function
# f(x) = a0 + a1*x + a2*x^2 + ...
# ============================================

def polynomial(x, coefficients):

    result = 0

    for power, coefficient in enumerate(coefficients):

        result += coefficient * (x ** power)

    return result % PRIME

# ============================================
# Modular Inverse
# Used in Lagrange Interpolation
# ============================================

def mod_inverse(a):

    return pow(a, -1, PRIME)

# ============================================
# Save Share to JSON File
# ============================================

def save_share(folder_path, admin_id, x, y):

    share_data = {
        "admin_id": admin_id,
        "x": x,
        "y": y
    }

    filename = os.path.join(
        folder_path,
        f"site_admin_{admin_id}.json"
    )

    with open(filename, "w") as file:
        json.dump(share_data, file, indent=4)

# ============================================
# Load Share from JSON File
# ============================================

def load_share(filepath):

    with open(filepath, "r") as file:

        data = json.load(file)

    return (data["x"], data["y"])

# ============================================
# Recover Secret using Lagrange Interpolation
# ============================================

def recover_secret(shares):

    secret = 0

    for j, (xj, yj) in enumerate(shares):

        numerator = 1
        denominator = 1

        for m, (xm, ym) in enumerate(shares):

            if m != j:

                numerator = (
                    numerator * (-xm)
                ) % PRIME

                denominator = (
                    denominator * (xj - xm)
                ) % PRIME

        lagrange_coefficient = (
            numerator * mod_inverse(denominator)
        ) % PRIME

        secret = (
            secret + (yj * lagrange_coefficient)
        ) % PRIME

    return secret