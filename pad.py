
"""
SMTPad
"""

import tkinter as tk
from tkinter.filedialog import askopenfilename, asksaveasfilename
# # import score
# # import cmn
# from lang import *
from lang import *
from cmn import *
from engine import render




def open_file():
    """Open a file for editing."""
    filepath = askopenfilename(
        filetypes=[("Text Files", "*.txt"), ("All Files", "*.*")]
    )
    if not filepath:
        return
    txt_edit.delete(1.0, tk.END)
    with open(filepath, "r") as input_file:
        text = input_file.read()
        txt_edit.insert(tk.END, text)
    pad.title(f"{CAPTION} - {filepath}")

def save_file():
    """Save the current file as a new file."""
    filepath = asksaveasfilename(
        defaultextension="txt",
        filetypes=[("Text Files", "*.txt"), ("All Files", "*.*")],
    )
    if not filepath:
        return
    with open(filepath, "w") as output_file:
        text = txt_edit.get(1.0, tk.END)
        output_file.write(text)
    pad.title(f"{CAPTION} - {filepath}")


def evalsrc(e):
    srctxt = txt_edit.get('1.0', 'end')
    env = make_env()
    for toplevel_expr in toplevel_exprs(index_tokens(tokenize_source(srctxt))):
        evalexp(read_from_tokens(toplevel_expr), env)


# paredit
def insert_rbracket(_):
    txt_edit.mark_gravity(tk.INSERT, tk.LEFT)
    txt_edit.insert(txt_edit.index(tk.INSERT), RBRACKET)
    txt_edit.mark_gravity(tk.INSERT, tk.RIGHT)

def insert_rdquote(_):
    txt_edit.mark_gravity(tk.INSERT, tk.LEFT)
    txt_edit.insert(txt_edit.index(tk.INSERT), '"')
    txt_edit.mark_gravity(tk.INSERT, tk.RIGHT)

def insert_rquote(_):
    txt_edit.mark_gravity(tk.INSERT, tk.LEFT)
    txt_edit.insert(txt_edit.index(tk.INSERT), "'")
    txt_edit.mark_gravity(tk.INSERT, tk.RIGHT)

CAPTION = "SMTPad"
pad = tk.Tk()
pad.title(CAPTION)
pad.rowconfigure(0, minsize=300, weight=1)
pad.columnconfigure(1, minsize=250, weight=1)

txt_edit = tk.Text(pad)
# fr_buttons = tk.Frame(pad, relief=tk.RAISED, bd=2)
# btn_open = tk.Button(fr_buttons, text="Open", command=open_file)
# btn_save = tk.Button(fr_buttons, text="Save As", command=save_file)

pad.bind("<Control_L>e", evalsrc)
pad.bind(LBRACKET, insert_rbracket)
pad.bind('"', insert_rdquote)
pad.bind("'", insert_rquote)


# btn_open.grid(row=0, column=0, sticky="ew", padx=5, pady=5)
# btn_save.grid(row=1, column=0, sticky="ew", padx=5)
# btn_eval.grid(row=2, column=0, sticky="ew", padx=5)

# fr_buttons.grid(row=0, column=0, sticky="ns")
txt_edit.grid(row=0, column=1, sticky="nsew")

if __name__ == "__main__":
	pad.mainloop()
