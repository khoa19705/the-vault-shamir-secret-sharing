import os
import random

from utils import (
    load_share,
    recover_secret
)

# ============================================
# SECRET RECOVERY PROCESS
# ============================================

def recover_secret_process():

    output = ""

    # ========================================
    # Project Paths
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

    # ========================================
    # Report File
    # ========================================

    report_path = os.path.join(
        shares_folder,
        "recovery_report.txt"
    )

    # ========================================
    # Load All Shares
    # ========================================

    all_shares = []

    for i in range(1, 6):

        share = load_share(
            os.path.join(
                shares_folder,
                f"site_admin_{i}.json"
            )
        )

        all_shares.append(share)

    # ========================================
    # Random Recovery Using 3 Shares
    # ========================================

    selected_shares = random.sample(
        all_shares,
        3
    )

    output += "====================================\n"
    output += " RECOVERING SECRET WITH 3 SHARES \n"
    output += "====================================\n\n"

    output += "Selected Shares:\n"

    for share in selected_shares:

        output += f"{share}\n"

    recovered_secret = recover_secret(
        selected_shares
    )

    # ========================================
    # Save Recovered Secret
    # ========================================

    recovered_key_path = os.path.join(
        shares_folder,
        "recovered_key.txt"
    )

    with open(recovered_key_path, "w") as file:

        file.write(str(recovered_secret))

    # ========================================
    # Load Original Secret
    # ========================================

    original_key_path = os.path.join(
        shares_folder,
        "original_key.txt"
    )

    with open(original_key_path, "r") as file:

        original_secret = int(file.read())

    # ========================================
    # Verify Recovery
    # ========================================

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
            "Recovered secret does NOT match.\n"
        )

    # ========================================
    # Failure Test with Random 2 Shares
    # ========================================

    two_shares = random.sample(
        all_shares,
        2
    )

    failed_secret = recover_secret(
        two_shares
    )

    failure_success = (
        failed_secret != original_secret
    )

    output += "\n====================================\n"
    output += " FAILURE TEST WITH 2 SHARES \n"
    output += "====================================\n\n"

    output += "Selected Shares:\n"

    for share in two_shares:

        output += f"{share}\n"

    output += (
        f"\nRecovered Value: "
        f"{failed_secret}\n"
    )

    if failure_success:

        output += (
            "\nSTATUS: FAILED AS EXPECTED\n"
        )

        output += (
            "2 shares are insufficient "
            "to recover the secret.\n"
        )

    else:

        output += (
            "\nSTATUS: UNEXPECTED\n"
        )

        output += (
            "Recovery should not work "
            "with only 2 shares.\n"
        )

    # ========================================
    # Write Recovery Report
    # ========================================

    with open(report_path, "w") as report:

        report.write(output)

    output += "\n====================================\n"
    output += " RECOVERY REPORT GENERATED \n"
    output += "====================================\n"

    output += f"{report_path}\n"

    return output

# ============================================
# Run Directly
# ============================================

if __name__ == "__main__":

    result = recover_secret_process()

    print(result)