import tkinter as tk
from tkinter import scrolledtext

from share_generator import generate_shares
from recovery_secret import recover_secret_process

# ============================================
# SHAMIR SECRET SHARING GUI APPLICATION
# ============================================

# ============================================
# GUI Window
# ============================================

root = tk.Tk()

root.title("The Vault - Shamir Secret Sharing")

root.geometry("900x700")

# ============================================
# Output Area
# ============================================

output_box = scrolledtext.ScrolledText(
    root,
    width=110,
    height=35
)

output_box.pack(padx=10, pady=10)

# ============================================
# Helper Function
# ============================================

def write_output(text):

    output_box.insert(tk.END, text + "\n")

    output_box.see(tk.END)

# ============================================
# GUI Actions
# ============================================

def gui_generate_shares():

    output_box.delete(1.0, tk.END)

    result = generate_shares()

    write_output(result)

def gui_recover_secret():

    output_box.delete(1.0, tk.END)

    result = recover_secret_process()

    write_output(result)

# ============================================
# Buttons
# ============================================

button_frame = tk.Frame(root)

button_frame.pack(pady=10)

generate_button = tk.Button(
    button_frame,
    text="Generate Shares",
    width=25,
    command=gui_generate_shares
)

generate_button.grid(
    row=0,
    column=0,
    padx=10
)

recover_button = tk.Button(
    button_frame,
    text="Recover Secret",
    width=25,
    command=gui_recover_secret
)

recover_button.grid(
    row=0,
    column=1,
    padx=10
)

# ============================================
# Run Application
# ============================================

root.mainloop()