# Import required Libraries
import os

import sys
import tkinter
from tkinter import *

import cv2
import dlib
import numpy as np

from Tool import Tool


class EyeTracking(Tool):

    def __init__(self, win, frame, back_callback):
        self.back_callback = back_callback

        # set font-parameter
        self.font = cv2.FONT_HERSHEY_COMPLEX
        self.fontScale = 1
        self.color = (255, 255, 255)
        self.thickness = 2

        # Execute super class constructor
        super().__init__(win, frame)

    def drawView(self):
        self.win.title("Webcam-Eyetracking")

        # set window-size
        self.win.geometry("820x550")
       # self.win.geometry('+300+85')

        # Canvas
        self.canvas = tkinter.Canvas(self.frame, highlightthickness=0, bd=0, bg='gray',
                                     width=820, height=550)
        self.canvas.pack()

        # buttons window
        schaltf1 = Button(self.canvas, text="Eyetracking starten", bg="grey", command=self.eyetrack).place(x=680, y=80)
        schaltf3 = Button(self.canvas, text="Schließen", bg="red", command=self.quit_eyetracking).place(x=700, y=380)
        l = Label(self.canvas, text="(Close Eyetracker with ESC)")
        l.place(x=655, y=120)

        self.win.mainloop()

    def quit_eyetracking(self):
        self.canvas.destroy()
        self.back_callback()

    def eyetrack(self):

        def shape_to_np(shape, dtype="int"):
            # initialize the list of (x, y)-coordinates
            coords = np.zeros((68, 2), dtype=dtype)
            # convert the 68 facial landmarks to (x, y)-coordinates
            for i in range(0, 68):
                coords[i] = (shape.part(i).x, shape.part(i).y)
            # return the list of (x, y)-coordinates
            return coords

        def eye_on_mask(mask, side):
            points = [shape[i] for i in side]
            points = np.array(points, dtype=np.int32)
            mask = cv2.fillConvexPoly(mask, points, 255)
            return mask

        def direction(thresh, mid, img, side, font, fontScale, color, thickness, right=False):
            cnts, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)
            try:
                cnt = max(cnts, key=cv2.contourArea)
                M = cv2.moments(cnt)
                cx = int(M['m10'] / M['m00'])
                cy = int(M['m01'] / M['m00'])
                if right:
                    cx += mid
                cv2.circle(img, (cx, cy), 4, (0, 0, 255), 1)
                # right eye
                if (side == 1):
                    xmiddle = (shape[39, 0] + shape[36, 0]) / 2
                    ymiddle = (shape[38, 1] + shape[40, 1]) / 2


                # horizontal direction
                if (cx < xmiddle - 1.5):
                    cv2.putText(img, "RIGHT", (200, 80), font, fontScale, color, thickness)
                elif (cx > xmiddle + 2.1):
                    cv2.putText(img, "LEFT", (200, 80), font, fontScale, color, thickness)
                else:
                    cv2.putText(img, "CENTER", (200, 80), font, fontScale, color, thickness)

                # vertical direction
                if (cy > shape[40, 1] - 5):
                    cv2.putText(img, "BOTTOM", (50, 80), font, fontScale, color, thickness)
                elif (cy < shape[38, 1] + 2.2):
                    cv2.putText(img, "TOP", (50, 80), font, fontScale, color, thickness)
                else:
                    cv2.putText(img, "CENTER", (50, 80), font, fontScale, color, thickness)

            except:
                pass

        detector = dlib.get_frontal_face_detector()
        # Check if MEIPASS attribute is available in sys else return current file path
        bundle_dir = getattr(sys, '_MEIPASS',
                             os.path.abspath(os.path.dirname(__file__)))
        path_to_data = os.path.abspath(os.path.join(bundle_dir, 'shape_predictor_68_face_landmarks.dat'))
        predictor = dlib.shape_predictor(path_to_data)

        left = [36, 37, 38, 39, 40, 41]
        right = [42, 43, 44, 45, 46, 47]
    # capture webcam (0 for default cam, 1 for extern)
        cam = cv2.VideoCapture(0)
        ret, img = cam.read()
        thresh = img.copy()

        cv2.namedWindow('Calibration')
        cv2.resizeWindow('Calibration', 600, 40)
        cv2.moveWindow('Calibration', 300, 0)

        kernel = np.ones((9, 9), np.uint8)
        cv2.createTrackbar('threshold', 'Calibration', 60, 130, self.nothing)

        while (True):
            ret, img = cam.read()
            gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
            rects = detector(gray, 1)
            for rect in rects:
                shape = predictor(gray, rect)
                shape = shape_to_np(shape)
                mask = np.zeros(img.shape[:2], dtype=np.uint8)
                mask = eye_on_mask(mask, left)
                mask = eye_on_mask(mask, right)
                mask = cv2.dilate(mask, kernel, 5)
                eyes = cv2.bitwise_and(img, img, mask=mask)
                mask = (eyes == [0, 0, 0]).all(axis=2)
                eyes[mask] = [255, 255, 255]
                mid = (shape[42][0] + shape[39][0]) // 2
                eyes_gray = cv2.cvtColor(eyes, cv2.COLOR_BGR2GRAY)
                threshold = cv2.getTrackbarPos('threshold', 'Calibration')
                _, thresh = cv2.threshold(eyes_gray, threshold, 255, cv2.THRESH_BINARY)
                thresh = cv2.erode(thresh, None, iterations=2)  # 1
                thresh = cv2.dilate(thresh, None, iterations=4)  # 2
                thresh = cv2.medianBlur(thresh, 3)  # 3
                thresh = cv2.bitwise_not(thresh)
                direction(thresh[:, 0:mid], mid, img, 1, self.font, self.fontScale, self.color, self.thickness)
                direction(thresh[:, mid:], mid, img, 2, self.font, self.fontScale, self.color, self.thickness, True)

            # show windows with eyetracker and calibration
            cv2.imshow('eyes', img)
            cv2.moveWindow('eyes', 300, 85)
            cv2.imshow("Calibration", thresh)
            cv2.resizeWindow('Calibration', 600, 40)

            key = cv2.waitKey(1)
            if key == 27:
                break

        cam.release()
        cv2.destroyAllWindows()

    def nothing(self, x):
        pass