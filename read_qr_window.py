import tkinter as tk
from PIL import Image, ImageTk
import cv2 as cv
import numpy as np
import math

import pyqrcode


class ReadWindow:
    ### Window Parameters
    WINDOW_SIZE_X = 1080
    WINDOW_SIZE_Y = 512
    WINDOW_SIZE_CONCAT = str(WINDOW_SIZE_X) + "x" + str(WINDOW_SIZE_Y)

    detected = False

    def __init__(self):
        self.window = tk.Tk()
        self.window.title("Multispectral QR Code")
        self.window.geometry(self.WINDOW_SIZE_CONCAT)

        self.cap = cv.VideoCapture(0)

        print(self.cap.read())
        self.canvas = tk.Canvas(self.window, width=self.cap.read()[1].shape[0], height=self.cap.read()[1].shape[1])
        self.canvas.pack()

        self.delay = 10
        self.update()

    # Display barcode and QR code location
    def display(self, img, bbox):
        img = cv.cvtColor(img, cv.COLOR_GRAY2BGR)
        n = len(bbox[0])
        pt2 = 0
        for j in range(n - 1):
            pt1 = (int(bbox[0][j][0]), int(bbox[0][j][1]))
            pt2 = (int(bbox[0][j+1][0]), int(bbox[0][j+1][1]))

            if math.sqrt((pt1[0] - pt2[0])**2 + (pt1[1] - pt2[1])**2) < 30:
                return

            cv.line(img, pt1, pt2, (255, 0, 255), 3)

        fpt1 = (int(bbox[0][0][0]), int(bbox[0][0][1]))
        if math.sqrt((fpt1[0] - pt2[0]) ** 2 + (fpt1[1] - pt2[1]) ** 2) < 30:
            return

        cv.line(img, fpt1, pt2, (255, 0, 255), 3)

        # Display results
        self.detected = True
        cv.imshow("Results", img)

    def update(self):
        tbc = True

        # Get a frame from the video source
        ret, frame = self.cap.read()
        frame = cv.cvtColor(frame, cv.COLOR_BGR2GRAY)
        frame[frame > 128] = 255
        frame[frame <= 127] = 0

        qrDecoder = cv.QRCodeDetector()

        # Detect and decode the qrcode
        data, bbox, _ = qrDecoder.detectAndDecode(frame)
        if bbox is not None:
            self.display(frame, bbox)
            if self.detected:
                tbc = False
        else:
            print("QR Code not detected")

        if ret:
            self.photo = ImageTk.PhotoImage(master=self.canvas, image=Image.fromarray(frame))
            self.canvas.create_image(0, 0, image=self.photo, anchor=tk.NW)
        if tbc:
            self.window.after(self.delay, self.update)
