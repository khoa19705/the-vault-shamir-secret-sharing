import random
import secrets
import json
import os

# ============================================
# SHAMIR SECRET SHARING - SHARE GENERATOR
# ============================================

# Parameters
N = 5   # Total shares
T = 3   # Threshold

# Large prime number for finite field operations
PRIME = 2**257 - 93

# ============================================
# Generate AES-256 Secret Key
# ============================================

secret = secrets.randbits(256)

print("====================================")
print(" AES-256 MASTER KEY ")
print("====================================")
print(secret)

# ============================================
# Generate Random Polynomial Coefficients
# f(x) = secret + a1*x + a2*x^2
# ============================================

coefficients = [secret]

for _ in range(T - 1):
    coefficients.append(random.randrange(1, PRIME))

print("\n====================================")
print(" POLYNOMIAL COEFFICIENTS ")
print("====================================")

for i, coeff in enumerate(coefficients):
    print(f"a{i} = {coeff}")

# ============================================
# Polynomial Function
# ============================================

def polynomial(x, coeffs):

    result = 0

    for power, coeff in enumerate(coeffs):
        result += coeff * (x ** power)

    return result % PRIME

# ============================================
# Generate Shares
# ============================================

shares = []

print("\n====================================")
print(" GENERATED SHARES ")
print("====================================")

for i in range(1, N + 1):

    x = i
    y = polynomial(x, coefficients)

    share = (x, y)

    shares.append(share)

    print(f"Admin {i}: {share}")

# ============================================
# Create Shares Folder
# ============================================

base_dir = os.path.dirname(os.path.abspath(__file__))

shares_folder = os.path.join(base_dir, "shares")

os.makedirs(shares_folder, exist_ok=True)

# ============================================
# Save Shares to JSON Files
# ============================================

for i, (x, y) in enumerate(shares, start=1):

    share_data = {
        "admin_id": i,
        "x": x,
        "y": y
    }

    filename = os.path.join(
        shares_folder,
        f"site_admin_{i}.json"
    )

    with open(filename, "w") as file:
        json.dump(share_data, file, indent=4)

    print(f"Saved: {filename}")

# ============================================
# Finished
# ============================================

print("\n====================================")
print(" SHARES SAVED SUCCESSFULLY ")
print("====================================")

print(f"Folder Location:")
print(shares_folder)