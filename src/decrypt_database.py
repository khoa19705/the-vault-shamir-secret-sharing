from Crypto.Cipher import AES
from Crypto.Util.Padding import unpad
import os

# ============================================
# Decrypt Database
# ============================================

def decrypt_database(secret):

    current_dir = os.path.dirname(
        os.path.abspath(__file__)
    )

    project_root = os.path.dirname(
        current_dir
    )

    # ========================================
    # Database Paths
    # ========================================

    encrypted_path = os.path.join(
        project_root,
        "database",
        "database.enc"
    )

    decrypted_path = os.path.join(
        project_root,
        "database",
        "database_decrypted.json"
    )

    # ========================================
    # Check Encrypted File
    # ========================================

    if not os.path.exists(encrypted_path):

        return (
            "Encrypted database file not found.\n"
            f"Expected: {encrypted_path}"
        )

    # ========================================
    # Read Encrypted File
    # ========================================

    with open(encrypted_path, "rb") as file:

        iv = file.read(16)

        ciphertext = file.read()

    # ========================================
    # Convert Secret to AES Key
    # ========================================

    key = secret.to_bytes(
        32,
        byteorder="big"
    )

    # ========================================
    # AES Decryption
    # ========================================

    cipher = AES.new(
        key,
        AES.MODE_CBC,
        iv
    )

    decrypted_raw = cipher.decrypt(
        ciphertext
    )

    # ========================================
    # Try Unpadding
    # ========================================

    try:

        decrypted_data = unpad(
            decrypted_raw,
            AES.block_size
        )

        status = (
            "Database decrypted successfully."
        )

    except Exception:

        # ====================================
        # Wrong Key
        # Save corrupted content for demo
        # ====================================

        decrypted_data = decrypted_raw

        status = (
            "WARNING: Invalid key detected.\n"
            "Database content is corrupted."
        )

    # ========================================
    # Save Decrypted Database
    # ========================================

    with open(decrypted_path, "wb") as file:

        file.write(decrypted_data)

    # ========================================
    # Finished
    # ========================================

    return (
        f"{status}\n"
        f"Saved: {decrypted_path}"
    )