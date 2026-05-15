from Crypto.Cipher import AES
from Crypto.Util.Padding import pad
import os

# ============================================
# Encrypt Database
# ============================================

def encrypt_database(secret):

    current_dir = os.path.dirname(
        os.path.abspath(__file__)
    )

    project_root = os.path.dirname(
        current_dir
    )

    database_path = os.path.join(
        project_root,
        "database",
        "database.json"
    )

    encrypted_path = os.path.join(
        project_root,
        "database",
        "database.enc"
    )

    # ========================================
    # Read Database
    # ========================================

    with open(database_path, "rb") as file:

        data = file.read()

    # ========================================
    # Convert Secret to AES Key
    # ========================================

    key = secret.to_bytes(32, byteorder="big")

    # ========================================
    # AES Encryption
    # ========================================

    cipher = AES.new(key, AES.MODE_CBC)

    ciphertext = cipher.encrypt(
        pad(data, AES.block_size)
    )

    # ========================================
    # Save Encrypted File
    # ========================================

    with open(encrypted_path, "wb") as file:

        file.write(cipher.iv)
        file.write(ciphertext)

    return (
        "Database encrypted successfully.\n"
        f"Saved: {encrypted_path}"
    )