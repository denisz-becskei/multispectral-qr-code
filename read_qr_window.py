import tkinter as tk

import cv2
from cv2 import cv2 as cv
from PIL import Image, ImageTk
import numpy as np
import math
from tkinter import filedialog as fd
from values import SIDE_PANEL_SIZE


class ReadWindow:
    # Window Parameters
    WINDOW_SIZE_X = 1080
    WINDOW_SIZE_Y = 576
    WINDOW_SIZE_CONCAT = str(WINDOW_SIZE_X) + "x" + str(WINDOW_SIZE_Y)

    color_ranges = [
        ((0, 50, 50), (10, 255, 255)),  # red
        ((170, 50, 50), (180, 255, 255)),  # red upper
        ((100, 50, 50), (130, 255, 255)),  # blue
        ((50, 50, 50), (70, 255, 255)),  # green
        ((130, 50, 50), (170, 255, 255)),  # magenta
        ((20, 50, 50), (50, 255, 255)),  # yellow
        ((70, 50, 50), (100, 255, 255)),  # cyan
        ((0, 0, 0), (180, 255, 50)),  # black
        ((0, 0, 231), (180, 30, 255))  # white
    ]

    struct = cv2.getStructuringElement(cv2.MORPH_RECT, (5, 5))

    main_colors = [
        (255, 0, 0),
        (0, 255, 0),
        (0, 0, 255)
    ]

    filetypes = (
        ('PNG Files', '*.png'),
        ('JPEG Files', '*.jpeg'),
        ('PDF Files', '*.pdf')
    )

    def __init__(self):
        self.image = None
        self.photo = None
        self.window = tk.Tk()
        self.window.title("Multispectral QR Code")
        self.window.geometry(self.WINDOW_SIZE_CONCAT)
        self.window.resizable(False, False)
        self.cap = cv.VideoCapture(0)
        self.presentation_iteration = 0
        self.open_image = None

        side_panel = tk.Canvas(self.window, height=SIDE_PANEL_SIZE[1], width=SIDE_PANEL_SIZE[0])
        side_panel.place(x=self.WINDOW_SIZE_X - SIDE_PANEL_SIZE[0], y=0)

        try:
            # self.canvas = tk.Canvas(self.window, width=self.cap.read()[1].shape[0], height=self.cap.read()[
            # 1].shape[1])
            self.canvas = tk.Canvas(self.window, width=480, height=480)
            self.canvas.pack(anchor=tk.CENTER, side=tk.TOP)
        except AttributeError:
            print("No connected webcam")
            # TODO: Add clear indication to user

        self.output_text = tk.Text(side_panel, width=31)
        self.output_text.pack()

        ### Add Menubar
        menubar = tk.Menu(self.window)
        file_menu = tk.Menu(menubar, tearoff=0)

        file_menu.add_command(label="Open...", command=self.open_file)
        file_menu.add_command(label="Exit", command=self.window.quit)
        menubar.add_cascade(label="File", menu=file_menu)

        self.window.config(menu=menubar)

        self.delay = 2000
        self.update()

    def update(self):
        tbc = True

        # Get a frame from the video source
        ret, frame = self.cap.read()

        if self.open_image is not None:
            frame = cv2.imread(self.open_image)

        original_frame = cv.cvtColor(frame, cv.COLOR_BGR2RGB)
        original_frame = cv2.resize(original_frame, (480, 480))

        self.image = self.masking_operation(original_frame)
        bits = [
            self.get_qr_of_color(
                [self.color_ranges[0], self.color_ranges[1], self.color_ranges[4], self.color_ranges[5]]),  # red
            self.get_qr_of_color([self.color_ranges[3], self.color_ranges[5], self.color_ranges[6]]),  # green
            self.get_qr_of_color([self.color_ranges[2], self.color_ranges[4], self.color_ranges[6]]),  # blue
        ]

        data = ""
        qcd = cv2.QRCodeDetector()

        for bit in bits:
            _, decoded_info, _, _ = qcd.detectAndDecodeMulti(bit)
            try:
                data += decoded_info[0]
            except IndexError:
                # TODO: no qr can be read
                pass
        if self.output_text.get("1.0", tk.END).strip() != data:
            self.output_text.configure(state='normal')
            self.output_text.delete('1.0', tk.END)
            self.output_text.insert(tk.INSERT, data)
            self.output_text.configure(state='disabled')
        presentation_look = self.present_qr_of_color(bits[self.presentation_iteration],
                                                     self.main_colors[self.presentation_iteration])

        self.presentation_iteration += 1
        if self.presentation_iteration == 3:
            self.presentation_iteration = 0

        if ret:
            frame = Image.fromarray(presentation_look)
            self.photo = ImageTk.PhotoImage(master=self.canvas, image=frame)
            self.canvas.create_image(480 // 2, 480 // 2, image=self.photo, anchor=tk.CENTER)
        if tbc:
            self.window.after(self.delay, self.update)

    def masking_operation(self, og_img):
        img = cv2.cvtColor(og_img, cv2.COLOR_RGB2HSV)

        # Create binary masks for each color range
        masks = []
        for color_range in self.color_ranges:
            lower, upper = np.array(color_range[0]), np.array(color_range[1])
            mask = cv2.inRange(img, lower, upper)
            masks.append(mask)

        # Combine masks
        combined_mask = np.zeros_like(masks[0])
        for mask in masks:
            combined_mask |= mask

        # Apply mask to image
        return cv2.bitwise_and(og_img, og_img, mask=combined_mask)

    def get_qr_of_color(self, ranges):
        img = cv2.cvtColor(self.image, cv2.COLOR_RGB2HSV)
        lower, upper = np.array(self.color_ranges[7][0]), np.array(self.color_ranges[7][1])
        black_mask = cv2.inRange(img, lower, upper)
        black_mask = cv2.bitwise_not(black_mask)
        black_masked = cv2.bitwise_and(img, img, mask=black_mask)
        _, _, black_colors = cv2.split(black_masked)
        black_colors[black_colors > 64] = 255
        black_colors[black_colors <= 64] = 0

        # Create binary masks for each color range
        masks = []
        for color_range in ranges:
            lower, upper = np.array(color_range[0]), np.array(color_range[1])
            mask = cv2.inRange(img, lower, upper)
            masks.append(mask)

        # Combine masks
        combined_mask = np.zeros_like(masks[0])
        for mask in masks:
            combined_mask |= mask

        masked = cv2.bitwise_and(self.image, self.image, mask=combined_mask)

        gray = cv2.cvtColor(masked, cv2.COLOR_RGB2GRAY)
        gray[gray != 0] = 255
        gray = cv2.bitwise_not(gray)

        pre_morphology = cv2.bitwise_and(black_colors, gray)
        dil1 = cv2.dilate(pre_morphology, self.struct)
        er1 = cv2.erode(dil1, self.struct)
        er2 = cv2.erode(er1, self.struct)
        dil2 = cv2.dilate(er2, self.struct)

        return dil2

    def filter_blacks_and_whites(self, original_frame, grayscale):
        _, thresh = cv2.threshold(grayscale, 220, 255, cv2.THRESH_BINARY)

        # Create a mask by inverting the thresholded image
        mask = cv2.bitwise_not(thresh)

        # Use the mask to set the light gray color to white
        original_frame[mask != 0] = (255, 255, 255)
        return original_frame

    def present_qr_of_color(self, qr, color):
        qr_present = cv2.cvtColor(qr, cv2.COLOR_GRAY2RGB)
        qr_present[qr == 0] = color
        return qr_present

    def open_file(self):
        self.open_image = fd.askopenfilename(title="Open File", initialdir="/", filetypes=self.filetypes)
        self.window.lift()
