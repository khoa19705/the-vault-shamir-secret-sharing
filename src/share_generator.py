import random
import secrets
import json
import os

from utils import (
    polynomial,
    PRIME
)

# ============================================
# SHARE GENERATION PROCESS
# ============================================

def generate_shares():

    output = ""

    # Parameters
    N = 5
    T = 3

    # ========================================
    # Generate AES-256 Secret Key
    # ========================================

    secret = secrets.randbits(256)

    output += "====================================\n"
    output += " AES-256 MASTER KEY \n"
    output += "====================================\n"
    output += f"{secret}\n"

    # ========================================
    # Generate Polynomial Coefficients
    # ========================================

    coefficients = [secret]

    for _ in range(T - 1):

        coefficients.append(
            random.randrange(1, PRIME)
        )

    output += "\n====================================\n"
    output += " POLYNOMIAL COEFFICIENTS \n"
    output += "====================================\n"

    for i, coeff in enumerate(coefficients):

        output += f"a{i} = {coeff}\n"

    # ========================================
    # Generate Shares
    # ========================================

    shares = []

    output += "\n====================================\n"
    output += " GENERATED SHARES \n"
    output += "====================================\n"

    for i in range(1, N + 1):

        x = i

        y = polynomial(x, coefficients)

        share = (x, y)

        shares.append(share)

        output += f"Admin {i}: {share}\n"

    # ========================================
    # Create Shares Folder
    # ========================================

    current_dir = os.path.dirname(
        os.path.abspath(__file__)
    )

    project_root = os.path.dirname(
        current_dir
    )

    shares_folder = os.path.join(
        project_root,
        "shares"
    )

    os.makedirs(
        shares_folder,
        exist_ok=True
    )

    # ========================================
    # Save Original Secret
    # ========================================

    original_key_path = os.path.join(
        shares_folder,
        "original_key.txt"
    )

    with open(original_key_path, "w") as file:

        file.write(str(secret))

    output += "\nOriginal key saved:\n"
    output += f"{original_key_path}\n"

    # ========================================
    # Save Shares
    # ========================================

    for i, (x, y) in enumerate(
        shares,
        start=1
    ):

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

            json.dump(
                share_data,
                file,
                indent=4
            )

        output += f"Saved: {filename}\n"

    # ========================================
    # Finished
    # ========================================

    output += "\n====================================\n"
    output += " SHARES SAVED SUCCESSFULLY \n"
    output += "====================================\n"

    output += f"{shares_folder}\n"

    return output

# ============================================
# Run Directly
# ============================================

if __name__ == "__main__":

    result = generate_shares()

    print(result)