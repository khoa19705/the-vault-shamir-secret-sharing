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

    try:

        cipher = AES.new(
            key,
            AES.MODE_CBC,
            iv
        )

        decrypted_data = unpad(
            cipher.decrypt(ciphertext),
            AES.block_size
        )

    except Exception as e:

        return (
            "Decryption failed.\n"
            f"Error: {str(e)}"
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
        "Database decrypted successfully.\n"
        f"Saved: {decrypted_path}"
    )