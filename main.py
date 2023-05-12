import os
import tkinter as tk
from tkinter.filedialog import asksaveasfile

import pyqrcode
from PIL import ImageTk, Image

from decision_methods import *
from menu_actions import new_doc
from read_qr_window import ReadWindow
from utils import get_hard_limit, merge_color_channels, create_qr_code
from values import WINDOW_SIZE_CONCAT, WINDOW_SIZE_X, SIDE_PANEL_SIZE, QR_CANVAS_SIZE, MODES, VERSIONS

img = None
generated = None


def create_image():
    """
    Creates the image seen on the UI.
    :return: void
    """
    text = input_text_field.get("1.0", "end").strip()
    # print("Encoding " + text)
    selected_version = int(base2.get().split(" ")[1])
    encoding = decide_encoding(text)
    # print("Selected Version is Version " + str(selected_version))
    # print("Selected Mode is " + encoding)
    if base.get() == MODES[0]:
        qr = pyqrcode.create(text, error="M", mode=encoding,
                             version=selected_version)
        qr.png('qr_to_show.png', scale=8)
    else:
        # print("Selected multispectral")
        hard_limit = get_hard_limit(selected_version, encoding)
        if len(text) < hard_limit:
            qr = pyqrcode.create(text, error="M", mode=encoding,
                                 version=selected_version)
            qr.png('qr_to_show.png', scale=8)
        elif hard_limit < len(text) < hard_limit * 2:
            text1 = text[0:hard_limit]
            text2 = text[hard_limit:]
            qr = create_qr_code(text1, selected_version, encoding)
            qr.png('qr1.png', scale=8, module_color=[255, 0, 0, 255])
            qr = create_qr_code(text2, selected_version, encoding)
            qr.png('qr2.png', scale=8, module_color=[0, 255, 0, 255])

            red_qr_code_raw = Image.open("qr1.png").convert("RGB")
            green_qr_code_raw = Image.open("qr2.png").convert("RGB")
            merge_color_channels(selected_version, red_qr_code_raw, green_qr_code_raw)

        elif hard_limit * 2 < len(text) < hard_limit * 3:
            text1 = text[0:hard_limit]
            text2 = text[hard_limit:hard_limit * 2]
            text3 = text[hard_limit * 2:]
            qr = create_qr_code(text1, selected_version, encoding)
            qr.png('qr1.png', scale=8, module_color=[255, 0, 0, 255])
            qr = create_qr_code(text2, selected_version, encoding)
            qr.png('qr2.png', scale=8, module_color=[0, 255, 0, 255])
            qr = create_qr_code(text3, selected_version, encoding)
            qr.png('qr3.png', scale=8, module_color=[0, 0, 255, 255])

            red_qr_code_raw = Image.open("qr1.png").convert("RGB")
            green_qr_code_raw = Image.open("qr2.png").convert("RGB")
            blue_qr_code_raw = Image.open("qr3.png").convert("RGB")

            merge_color_channels(selected_version, red_qr_code_raw, green_qr_code_raw, blue_qr_code_raw)

    global img, generated
    img = None
    generated_code = Image.open("qr_to_show.png").resize((370, 370))
    generated = generated_code
    img = ImageTk.PhotoImage(generated_code)

    qr_canvas.delete("all")
    qr_canvas.create_image(0, 0, anchor="nw", image=img)


def change_version_states(event):
    """
    For locking down versions that are impossible to create depending on the length of the text. This is bound to the
    text field.
    :param event: On Keypress
    :return: void
    """
    text = input_text_field.get("1.0", "end").strip()
    current_encoding = decide_encoding(text)
    # print("Current Encoding is " + current_encoding)
    smallest_available_version = decide_smallest_available_version(current_encoding, text,
                                                                   base.get().strip() == "Multispectral")
    # print("Smallest available version is Version " + str(smallest_available_version))
    for option in range(0, 28):
        dropdown2['menu'].entryconfigure(option, state="normal")
    base2.set(VERSIONS[0])
    if smallest_available_version > 1:
        for option in range(0, smallest_available_version - 1):
            dropdown2['menu'].entryconfigure(option, state="disabled")
        base2.set(VERSIONS[smallest_available_version - 1])


def spawn_window():
    reader_window = ReadWindow()


def start_anew():
    new_doc(qr_canvas, input_text_field, base, base2)


def save_image(ext):
    if ext == "png":
        description = "PNG (*.PNG;*.PNG)"
    elif ext == "pdf":
        description = "PDF Document"
    else:
        print("You are not supposed to see this")
        description = "null"

    f = asksaveasfile(initialfile='Untitled.' + ext,
                      defaultextension=".png", filetypes=[(description, "*." + ext), ("All Files", "*.*")], mode="w")
    global generated
    if f and generated is not None:
        abs_path = os.path.abspath(f.name)
        generated.save(abs_path)

        # TODO: else

        # TODO: saved file hogged by Python


### Window Creation
window = tk.Tk()
window.title("Multispectral QR Code")
window.geometry(WINDOW_SIZE_CONCAT)
window.resizable(False, False)

### Side Panel
side_panel = tk.Canvas(window, height=SIDE_PANEL_SIZE[1], width=SIDE_PANEL_SIZE[0])
side_panel.place(x=WINDOW_SIZE_X - SIDE_PANEL_SIZE[0], y=0)

### Text Field
input_text_field = tk.Text(side_panel, height=5, width=31)
input_text_field.pack()
input_text_field.bind("<KeyRelease>", change_version_states)

### Dropdown for Mode Selection
base = tk.StringVar(side_panel)
base.set(MODES[0])

dropdown = tk.OptionMenu(side_panel, base, *MODES, command=change_version_states)
dropdown.pack()

### Dropdown for Version Selection
base2 = tk.StringVar(side_panel)
base2.set(VERSIONS[0])

dropdown2 = tk.OptionMenu(side_panel, base2, *VERSIONS)
dropdown2.pack()

### Button for QR Creation
create_btn = tk.Button(side_panel, height=2, width=25, text="Create", command=create_image)
create_btn.pack()

### Read QR Code
read_btn = tk.Button(side_panel, height=2, width=25, text="Read", command=spawn_window)
read_btn.pack()

### Place for the QR Code
qr_canvas = tk.Canvas(window, bg="#ffffff", height=QR_CANVAS_SIZE, width=QR_CANVAS_SIZE)
qr_canvas.place(x=WINDOW_SIZE_X / 2 - QR_CANVAS_SIZE, y=16)

### Add Menubar
menubar = tk.Menu(window)
file_menu = tk.Menu(menubar, tearoff=0)
file_menu.add_command(label="New", command=start_anew)
file_menu.add_command(label="Save...", command=lambda: save_image("png"))
file_menu.add_command(label="Export...", command=lambda: save_image("pdf"))
file_menu.add_command(label="Exit", command=window.quit)
menubar.add_cascade(label="File", menu=file_menu)

window.config(menu=menubar)
window.mainloop()
