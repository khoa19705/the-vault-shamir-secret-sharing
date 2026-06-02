import os
import requests

from decrypt_database import decrypt_database

from utils import (
    recover_secret
)

NODES = [
    "http://localhost:3001/share",
    "http://localhost:3002/share",
    "http://localhost:3003/share",
    "http://localhost:3004/share",
    "http://localhost:3005/share"
]

def recover_secret_process():

    output = ""

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

    report_path = os.path.join(
        shares_folder,
        "recovery_report.txt"
    )

    all_shares = []

    output += "====================================\n"
    output += " LOADING AVAILABLE NODES \n"
    output += "====================================\n\n"

    for index, node_url in enumerate(
        NODES,
        start=1
    ):

        try:

            response = requests.get(
                node_url,
                timeout=3
            )

            if response.status_code == 200:

                data = response.json()

                share = (
                    int(data["x"]),
                    int(data["y"])
                )

                all_shares.append(share)

                output += (
                    f"ONLINE : node{index}\n"
                )

            else:

                output += (
                    f"OFFLINE: node{index}\n"
                )

        except Exception:

            output += (
                f"OFFLINE: node{index}\n"
            )

    output += "\n"

    output += (
        f"Available Shares: "
        f"{len(all_shares)}/5\n"
    )

    original_key_path = os.path.join(
        shares_folder,
        "original_key.txt"
    )

    with open(original_key_path, "r") as file:

        original_secret = int(file.read())

    if len(all_shares) > 0:

        selected_shares = all_shares

        output += "\n====================================\n"

        output += (
            f" RECOVERING SECRET WITH "
            f"{len(selected_shares)} SHARES \n"
        )

        output += "====================================\n\n"

        output += "Selected Shares:\n"

        for share in selected_shares:

            output += f"{share}\n"

        recovered_secret = recover_secret(
            selected_shares
        )

        recovered_key_path = os.path.join(
            shares_folder,
            "recovered_key.txt"
        )

        with open(recovered_key_path, "w") as file:

            file.write(str(recovered_secret))

        recovery_success = (
            original_secret == recovered_secret
        )

        output += "\n====================================\n"
        output += " VERIFYING RECOVERY \n"
        output += "====================================\n"

        output += (
            f"Original Secret : "
            f"{original_secret}\n"
        )

        output += (
            f"Recovered Secret: "
            f"{recovered_secret}\n"
        )

        if recovery_success:

            output += "\nSTATUS: SUCCESS\n"

            output += (
                "Recovered secret is CORRECT.\n"
            )

        else:

            output += "\nSTATUS: FAILED\n"

            output += (
                "Recovered secret is INVALID.\n"
            )

        output += "\n====================================\n"
        output += " DATABASE DECRYPTION TEST \n"
        output += "====================================\n"

        try:

            decrypt_result = decrypt_database(
                recovered_secret
            )

            output += "\n"
            output += decrypt_result
            output += "\n"

            if recovery_success:

                output += (
                    "\nDatabase decrypted successfully "
                    "with correct key.\n"
                )

            else:

                output += (
                    "\nWARNING: Database decrypted "
                    "with invalid key.\n"
                )

        except Exception as e:

            output += (
                f"\nDecryption Failed: "
                f"{str(e)}\n"
            )

            output += (
                "Wrong key could not decrypt "
                "database.\n"
            )

    else:

        output += "\n====================================\n"
        output += " RECOVERY FAILED \n"
        output += "====================================\n"

        output += (
            "No shares available.\n"
        )

    with open(report_path, "w") as report:

        report.write(output)

    output += "\n====================================\n"
    output += " RECOVERY REPORT GENERATED \n"
    output += "====================================\n"

    output += f"{report_path}\n"

    return output

if __name__ == "__main__":

    result = recover_secret_process()

    print(result)