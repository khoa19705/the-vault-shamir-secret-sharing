import secrets
import json
import os

from encrypt_database import encrypt_database

from utils import (
    polynomial,
    PRIME
)

# ============================================
# SHARE GENERATION PROCESS
# ============================================

def generate_shares():

    output = ""

    # ========================================
    # Parameters
    # ========================================

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
            secrets.randbelow(PRIME - 1) + 1
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
    # Project Paths
    # ========================================

    current_dir = os.path.dirname(
        os.path.abspath(__file__)
    )

    project_root = os.path.dirname(
        current_dir
    )

    # ========================================
    # Save Original Secret
    # ========================================

    shares_folder = os.path.join(
        project_root,
        "shares"
    )

    os.makedirs(
        shares_folder,
        exist_ok=True
    )

    original_key_path = os.path.join(
        shares_folder,
        "original_key.txt"
    )

    with open(original_key_path, "w") as file:

        file.write(str(secret))

    output += "\nOriginal key saved:\n"
    output += f"{original_key_path}\n"

    # ========================================
    # Create Distributed Nodes
    # ========================================

    nodes_folder = os.path.join(
        project_root,
        "nodes"
    )

    os.makedirs(
        nodes_folder,
        exist_ok=True
    )

    # ========================================
    # Save Shares into Node Folders
    # ========================================

    output += "\n====================================\n"
    output += " DISTRIBUTING SHARES TO NODES \n"
    output += "====================================\n"

    for i, (x, y) in enumerate(
        shares,
        start=1
    ):

        # ------------------------------------
        # Create Node Folder
        # ------------------------------------

        node_folder = os.path.join(
            nodes_folder,
            f"node{i}"
        )

        os.makedirs(
            node_folder,
            exist_ok=True
        )

        # ------------------------------------
        # Share Data
        # ------------------------------------

        share_data = {
            "admin_id": i,
            "x": str(x),
            "y": str(y)
        }

        # ------------------------------------
        # Save Share
        # ------------------------------------

        filename = os.path.join(
            node_folder,
            "share.json"
        )

        with open(filename, "w") as file:

            json.dump(
                share_data,
                file,
                indent=4
            )

        output += (
            f"Node{i} received share:\n"
        )

        output += f"{filename}\n\n"

    # ========================================
    # Finished
    # ========================================

    output += "====================================\n"
    output += " DISTRIBUTION COMPLETED \n"
    output += "====================================\n"

    output += (
        "Shares distributed across "
        "5 independent nodes.\n"
    )

    encrypt_result = encrypt_database(secret)

    output += "\n"
    output += encrypt_result
    output += "\n"
    
    return output

# ============================================
# Run Directly
# ============================================

if __name__ == "__main__":

    result = generate_shares()

    print(result)