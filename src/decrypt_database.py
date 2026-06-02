from Crypto.Cipher import AES
from Crypto.Util.Padding import unpad
import os

def decrypt_database(secret):

    current_dir = os.path.dirname(
        os.path.abspath(__file__)
    )

    project_root = os.path.dirname(
        current_dir
    )

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

    if not os.path.exists(encrypted_path):

        return (
            "Encrypted database file not found.\n"
            f"Expected: {encrypted_path}"
        )

    with open(encrypted_path, "rb") as file:

        iv = file.read(16)

        ciphertext = file.read()

    key = secret.to_bytes(
        32,
        byteorder="big"
    )

    cipher = AES.new(
        key,
        AES.MODE_CBC,
        iv
    )

    decrypted_raw = cipher.decrypt(
        ciphertext
    )

    try:

        decrypted_data = unpad(
            decrypted_raw,
            AES.block_size
        )

        status = (
            "Database decrypted successfully."
        )

    except Exception:

        decrypted_data = decrypted_raw

        status = (
            "WARNING: Invalid key detected.\n"
            "Database content is corrupted."
        )

    with open(decrypted_path, "wb") as file:

        file.write(decrypted_data)

    return (
        f"{status}\n"
        f"Saved: {decrypted_path}"
    )