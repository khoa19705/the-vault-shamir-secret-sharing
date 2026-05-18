import os
import subprocess
import tkinter as tk
import threading

from tkinter import (
    scrolledtext,
    ttk
)

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

root.geometry("1200x900")

root.resizable(True, True)

# ============================================
# Title
# ============================================

title_label = tk.Label(
    root,
    text="THE VAULT - DISTRIBUTED SECRET SYSTEM",
    font=("Arial", 18, "bold")
)

title_label.pack(pady=10)

# ============================================
# Progress Bar
# ============================================

progress = ttk.Progressbar(
    root,
    orient="horizontal",
    length=500,
    mode="determinate"
)

progress.pack(pady=10)

# ============================================
# Output Area
# ============================================

output_box = scrolledtext.ScrolledText(
    root,
    width=140,
    height=25
)

output_box.pack(
    padx=10,
    pady=10
)

# ============================================
# Helper Functions
# ============================================

def write_output(text):

    output_box.insert(
        tk.END,
        text + "\n"
    )

    output_box.see(tk.END)

# --------------------------------------------

def update_progress(value):

    progress["value"] = value

    root.update_idletasks()

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
            cwd=node_path,
            shell=True
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

    except:
        pass

    if node_number in node_processes:

        try:

            process = node_processes[node_number]

            process.terminate()

            del node_processes[node_number]

        except:
            pass

    write_output(
        f"Node {node_number} stopped."
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
    update_progress(0)
    write_output("====================================")
    write_output(" GENERATING NEW SHARES ")
    write_output("====================================\n")

    def task():
        update_progress(10)
        stop_all_nodes()
        update_progress(30)
        result = generate_shares()
        write_output(result)
        update_progress(70)
        start_all_nodes()
        update_progress(100)
        write_output("\nAll nodes restarted with latest shares.")
        root.after(1000, lambda: update_progress(0))

    threading.Thread(target=task, daemon=True).start()

# --------------------------------------------

def gui_recover_secret():
    output_box.delete(1.0, tk.END)
    update_progress(0)
    write_output("Recovering secret...\n")

    def task():
        update_progress(40)
        result = recover_secret_process()
        update_progress(100)
        write_output(result)
        root.after(1000, lambda: update_progress(0))

    threading.Thread(target=task, daemon=True).start()
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
    bg="lightblue",
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
    bg="khaki",
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
    bg="orange",
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

for i in range(1, 6):

    node_label = tk.Label(
        node_frame,
        text=f"Node {i}",
        width=15,
        font=("Arial", 10, "bold")
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
# Global Controls
# ============================================

control_frame = tk.Frame(root)

control_frame.pack(pady=20)

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