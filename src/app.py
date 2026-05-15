import os
import subprocess
import tkinter as tk
from tkinter import scrolledtext

import requests

from share_generator import generate_shares
from recovery_secret import recover_secret_process

# ============================================
# SHAMIR SECRET SHARING GUI APPLICATION
# ============================================

# ============================================
# Project Paths
# ============================================

BASE_DIR = os.path.dirname(
    os.path.abspath(__file__)
)

PROJECT_ROOT = os.path.dirname(
    BASE_DIR
)

# ============================================
# Store Running Node Processes
# ============================================

node_processes = {}

# ============================================
# GUI Window
# ============================================

root = tk.Tk()

root.title(
    "The Vault - Shamir Secret Sharing"
)

# Bigger window
root.geometry("1200x850")

# Allow resize
root.resizable(True, True)

# ============================================
# Output Area
# ============================================

output_box = scrolledtext.ScrolledText(
    root,
    width=135,
    height=25
)

output_box.pack(
    padx=10,
    pady=10
)

# ============================================
# Helper Function
# ============================================

def write_output(text):

    output_box.insert(
        tk.END,
        text + "\n"
    )

    output_box.see(tk.END)

# ============================================
# Node Controls
# ============================================

def start_node(node_number):

    if node_number in node_processes:

        write_output(
            f"Node {node_number} already running."
        )

        return

    node_path = os.path.join(
        PROJECT_ROOT,
        "nodes",
        f"node{node_number}"
    )

    try:

        process = subprocess.Popen(
            ["node", "server.js"],
            cwd=node_path
        )

        node_processes[node_number] = process

        write_output(
            f"Node {node_number} started."
        )

    except Exception as e:

        write_output(
            f"Failed to start Node "
            f"{node_number}: {str(e)}"
        )

# --------------------------------------------

def stop_node(node_number):

    port = 3000 + node_number

    try:

        requests.get(
            f"http://localhost:{port}/shutdown",
            timeout=2
        )

        write_output(
            f"Node {node_number} stopped."
        )

        if node_number in node_processes:

            del node_processes[node_number]

    except Exception as e:

        write_output(
            f"Failed to stop Node "
            f"{node_number}: {str(e)}"
        )

# --------------------------------------------

def start_all_nodes():

    write_output(
        "\nStarting all nodes...\n"
    )

    for i in range(1, 6):

        start_node(i)

# --------------------------------------------

def stop_all_nodes():

    write_output(
        "\nStopping all nodes...\n"
    )

    for i in range(1, 6):

        stop_node(i)

# --------------------------------------------

def check_nodes():

    output_box.delete(1.0, tk.END)

    write_output(
        "===================================="
    )

    write_output(
        " NODE STATUS "
    )

    write_output(
        "====================================\n"
    )

    for i in range(1, 6):

        port = 3000 + i

        try:

            response = requests.get(
                f"http://localhost:{port}/health",
                timeout=2
            )

            if response.status_code == 200:

                write_output(
                    f"Node {i}: ONLINE"
                )

            else:

                write_output(
                    f"Node {i}: OFFLINE"
                )

        except:

            write_output(
                f"Node {i}: OFFLINE"
            )

# ============================================
# GUI Actions
# ============================================

def gui_generate_shares():

    output_box.delete(1.0, tk.END)

    write_output(
        "===================================="
    )

    write_output(
        " GENERATING NEW SHARES "
    )

    write_output(
        "====================================\n"
    )

    # Stop old nodes
    stop_all_nodes()

    # Generate new shares
    result = generate_shares()

    write_output(result)

    # Restart nodes
    start_all_nodes()

    write_output(
        "\nAll nodes restarted "
        "with latest shares."
    )

# --------------------------------------------

def gui_recover_secret():

    output_box.delete(1.0, tk.END)

    result = recover_secret_process()

    write_output(result)

# ============================================
# Main Buttons
# ============================================

main_button_frame = tk.Frame(root)

main_button_frame.pack(pady=10)

generate_button = tk.Button(
    main_button_frame,
    text="Generate Shares",
    width=25,
    height=2,
    command=gui_generate_shares
)

generate_button.grid(
    row=0,
    column=0,
    padx=10,
    pady=5
)

recover_button = tk.Button(
    main_button_frame,
    text="Recover Secret",
    width=25,
    height=2,
    command=gui_recover_secret
)

recover_button.grid(
    row=0,
    column=1,
    padx=10,
    pady=5
)

check_button = tk.Button(
    main_button_frame,
    text="Check Nodes",
    width=25,
    height=2,
    command=check_nodes
)

check_button.grid(
    row=0,
    column=2,
    padx=10,
    pady=5
)

# ============================================
# Node Controls
# ============================================

node_frame = tk.Frame(root)

node_frame.pack(pady=10)

# Headers
header1 = tk.Label(
    node_frame,
    text="Node",
    font=("Arial", 10, "bold")
)

header1.grid(
    row=0,
    column=0,
    padx=10,
    pady=5
)

header2 = tk.Label(
    node_frame,
    text="Start",
    font=("Arial", 10, "bold")
)

header2.grid(
    row=0,
    column=1,
    padx=10,
    pady=5
)

header3 = tk.Label(
    node_frame,
    text="Stop",
    font=("Arial", 10, "bold")
)

header3.grid(
    row=0,
    column=2,
    padx=10,
    pady=5
)

# Node Buttons
for i in range(1, 6):

    node_label = tk.Label(
        node_frame,
        text=f"Node {i}",
        width=15
    )

    node_label.grid(
        row=i,
        column=0,
        padx=5,
        pady=5
    )

    start_btn = tk.Button(
        node_frame,
        text="START",
        width=15,
        bg="lightgreen",
        command=lambda n=i: start_node(n)
    )

    start_btn.grid(
        row=i,
        column=1,
        padx=5,
        pady=5
    )

    stop_btn = tk.Button(
        node_frame,
        text="STOP",
        width=15,
        bg="tomato",
        command=lambda n=i: stop_node(n)
    )

    stop_btn.grid(
        row=i,
        column=2,
        padx=5,
        pady=5
    )

# ============================================
# Start / Stop All Buttons
# ============================================

control_frame = tk.Frame(root)

control_frame.pack(pady=15)

start_all_button = tk.Button(
    control_frame,
    text="START ALL NODES",
    width=25,
    height=2,
    bg="lightgreen",
    command=start_all_nodes
)

start_all_button.grid(
    row=0,
    column=0,
    padx=15
)

stop_all_button = tk.Button(
    control_frame,
    text="STOP ALL NODES",
    width=25,
    height=2,
    bg="tomato",
    command=stop_all_nodes
)

stop_all_button.grid(
    row=0,
    column=1,
    padx=15
)

# ============================================
# Run Application
# ============================================

root.mainloop()