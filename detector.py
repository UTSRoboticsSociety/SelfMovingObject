import numpy as np
import argparse
import cv2

class ColorPicker:
    def __init__(self):
        # initialize the list of reference points and boolean indicating
        # whether cropping is being performed or not
        self.refPt = []
        self.cropping = False
        self.font = cv2.FONT_HERSHEY_SIMPLEX

        # Snapshot
        self.work_image = []

    def click_and_crop(self, event, x, y, flags, param):

        # if the left mouse button was clicked, record the starting
        # (x, y) coordinates and indicate that cropping is being
        # performed
        if event == cv2.EVENT_LBUTTONDOWN:
            self.refPt = [(x, y)]
            self.cropping = True

        # check to see if the left mouse button was released
        elif event == cv2.EVENT_LBUTTONUP:
            # record the ending (x, y) coordinates and indicate that
            # the cropping operation is finished
            self.refPt.append((x, y))
            self.cropping = False

            # draw a rectangle around the region of interest
            cv2.rectangle(self.work_image, self.refPt[0], self.refPt[1], (0, 255, 0), 2)
            cv2.imshow("image", self.work_image)

    def select_color(self, image, message):

        self.refPt = [(0, 0)]

        hsvUpper = np.array([1, 1, 1])
        hsvLower = np.array([1, 1, 1])

        # load the image, clone it, and setup the mouse callback function

        self.work_image = cv2.imread('model.jpg')
        if image is not None:
            self.work_image = image

        cv2.putText(self.work_image, message, (100, 100), self.font, 2, (255, 255, 255), 2)
        clone = self.work_image.copy()
        cv2.namedWindow("image")
        cv2.setMouseCallback("image", self.click_and_crop)

        # keep looping until the 'q' key is pressed
        while True:
            # display the image and wait for a keypress
            cv2.imshow("image", self.work_image)
            key = cv2.waitKey(1) & 0xFF

            # if the 'r' key is pressed, reset the cropping region
            if key == ord("r"):
                self.work_image = clone.copy()

            # if the 'c' key is pressed, break from the loop
            elif key == ord("c"):
                # if there are two reference points, then crop the region of interest
                # from the image and display it
                if len(self.refPt) == 2:
                    roi = clone[self.refPt[0][1]:self.refPt[1][1], self.refPt[0][0]:self.refPt[1][0]]

                    hsv = cv2.cvtColor(roi, cv2.COLOR_BGR2HSV)
                    cv2.imshow("HSV", hsv)
                    average_color_per_row = np.average(hsv, axis=0)
                    average_color = np.average(average_color_per_row, axis=0)
                    average_color = np.uint8(average_color)
                    # debug print(average_color)
                    cv2.imshow("ROI", roi)

                    hsvUpper = np.array([average_color[0] + 15, average_color[1] + 180, average_color[2] + 130])
                    hsvLower = np.array([average_color[0] - 15, average_color[1] - 20, average_color[2] - 130])

                    # debug print("HSV UPPER is " + str(hsvUpper))
                    # debug print("HSV Lower is " + str(hsvLower))

            elif key == ord("q"):
                break

        # close all open windows
        cv2.destroyAllWindows()

        return hsvUpper, hsvLower

# Name of Video to Open. Works well on 1,2,6
videonumber = 1
url = ('Videos/video' + str(videonumber) + '.mp4')


def acquire_image(camera):
    # Load previously saved calibration data
    # This is to get rid of fish eye from MS USB Camera
    with np.load('calib.npz') as X:
        mtx, dist, _, _ = [X[i] for i in ('mtx', 'dist', 'rvecs', 'tvecs')]

    # grab the current frame
    grabbed, frame = camera.read()

    h, w = frame.shape[:2]

    # Get new camera matrix based off old calibration data
    newcameramtx, roi = cv2.getOptimalNewCameraMatrix(mtx, dist, (w, h), 1, (w, h))

    # Undistort the camera image based off calibration
    dst = cv2.undistort(frame, mtx, dist, None, newcameramtx)

    #  crop the image
    x, y, w, h = roi
    dst = dst[y:y + h, x:x + w]

    # Debug - Show Raw camera image
    # cv2.imshow('RAW', dst)

    # Apply a bilateral filter to the image to smooth out color gradients and highlight line edges
    # smooth = cv2.bilateralFilter(dst, 10, 75, 75)

    # resize the frame, blur it, and convert it to the HSV
    # color space
    # frame = imutils.resize(dst, width=1280)

    return dst

def mask_colors(frame, hsvUpper, hsvLower):
    # blurred = cv2.GaussianBlur(dst, (5, 5), 0)
    # thresh = cv2.threshold(blurred, 60, 255, cv2.THRESH_BINARY)[1]
    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

    # hsv = cv2.bilateralFilter(hsv,9,75,75)

    # Debug - Show HSV converted image
    # cv2.imshow('Thresh', hsv)

    # construct a mask for the color "green", then perform
    # a series of dilations and erosions to remove any small
    # blobs left in the mask
    mask = cv2.inRange(hsv, hsvLower, hsvUpper)
    mask = cv2.erode(mask, None, iterations=2)
    mask = cv2.dilate(mask, None, iterations=2)
    # Debug - Show Masked Image
    # cv2.imshow('Mask', mask)

    return mask

# returns center over the lane detecting lines
def laneDetect(numbers, width):
    numbers = numbers.flatten()
    value = 0
    count = 0
    for i in range(width):
        if (numbers[i] > 0):
            value = value + 1 * i
            count = count + 1
    if(count > 0):
        value = (int) (value / count)
    return value


def main():
    # Loading Video
    #cap = cv2.VideoCapture(url)
    cap = cv2.VideoCapture(0)
    image = cv2.imread('image.png')
    height, width = image.shape[:2]
    #image = cv2.resize(image,(2*width, 2*height), interpolation = cv2.INTER_CUBIC)

    #HSVMethod boolean variable determines weather it uses KWANGS colour select mehod or james' rgb HSVMethod
    #For better results set to False
    HSVMethod = False

    if(HSVMethod):
        # Pick the lane colors and object color
        rightupper, rightlower = ColorPicker().select_color(image.copy(), "select right lane")
        leftupper, leftlower = ColorPicker().select_color(image.copy(), "select left lane")
        objectupper, objectlower = ColorPicker().select_color(image.copy(), "select select object")


    #These values are the width and height of lane detection lines
    height = 450
    width = 300
    lx1 = 0 # ~ lx1 is is left x coord of the first line
    rx1 = lx1 + width
    lx2 = 919 - rx1
    rx2 = 919 - lx1

    #initial positions of detection lines
    lv = int (width / 2)
    rv = int (width / 2)

    while(True):
        if (cap.isOpened()):
            try:
                # Reads image of video and adds border to remove horizon
                image = acquire_image(cap)
                bordersize = 330
                image2 = image[bordersize:720,0:960]
                image2 = cv2.copyMakeBorder(image2, top = bordersize, bottom = 0, left = 0, right = 0, borderType = cv2.BORDER_CONSTANT, value = [0,0,0])

                if(HSVMethod): #Kwangs Method
                    # Define Colour boundaries and apply masks
                    # Set to HSV
                    grey_image = cv2.cvtColor(image2, cv2.COLOR_BGR2GRAY)

                    mask_right = mask_colors(image, rightupper, rightlower)
                    mask_left = mask_colors(image, leftupper, leftlower)
                    mask_object = mask_colors(image, objectupper, objectlower)

                    mask_set_lane = cv2.bitwise_or(mask_right, mask_left)
                    mask_set_object = cv2.bitwise_or(mask_set_lane, mask_object)

                    mask_image = cv2.bitwise_and(grey_image, mask_set_object)

                    #need 3 colour chanels for hstack
                    mask_image = cv2.cvtColor(mask_image, cv2.COLOR_GRAY2BGR)

                if(not HSVMethod): # James' Method
                    # Define Colour boundaries and apply masks
                    # Will need to work with hsl values instead of rgb for better accuracy
                    grey_image = cv2.cvtColor(image2, cv2.COLOR_BGR2GRAY)
                    lower_yellow = np.array([100,200,200], dtype = "uint8")
                    upper_yellow = np.array([180,255,255], dtype = "uint8")
                    lower_blue = np.array([100, 40, 4], dtype="uint8")
                    upper_blue = np.array([255, 185, 80], dtype="uint8")
                    mask_blue = cv2.inRange(image, lower_blue, upper_blue)
                    mask_yellow = cv2.inRange(image, lower_yellow, upper_yellow)
                    mask_yw = cv2.bitwise_or(mask_blue, mask_yellow)

                    mask_image = cv2.bitwise_and(grey_image, mask_yw)
                    mask_image = cv2.cvtColor(mask_image, cv2.COLOR_GRAY2BGR) #need 3 colour chanels for hstack


                # Smooth out the image
                kernel_size = 5
                blur_image = cv2.GaussianBlur(mask_image, (kernel_size, kernel_size), 0)


                # Basic Edge Detection (not implemented)
                low_threshold = 50
                high_threshold = 150
                canny_image = cv2.Canny(blur_image, low_threshold, high_threshold)
                canny_image = cv2.cvtColor(canny_image, cv2.COLOR_GRAY2BGR)


                #grabs thin line of pixels for lane detection
                leftPixels =  cv2.cvtColor(blur_image[height:height + 1,lx1:rx1], cv2.COLOR_BGR2GRAY)
                rightPixels =  cv2.cvtColor(blur_image[height:height + 1,lx2:rx2], cv2.COLOR_BGR2GRAY)
                if(laneDetect(leftPixels, width) > 0 or lv == None):
                    lv = laneDetect(leftPixels, width)
                if(laneDetect(rightPixels, width) > 0 or rv == None):
                    rv = laneDetect(rightPixels, width)


                # Draw lines over the image for lane detection
                leftline = lx1 + lv
                rightline = lx2 + rv
                midline = (int)((rightline + leftline) / 2)
                cv2.line(blur_image, (lx1,height), (rx1, height), (0,255,0), 2, 8, 0)
                cv2.line(blur_image, (lx2,height), (rx2, height), (0,255,0), 2, 8, 0)
                cv2.line(blur_image, ((leftline), height - 25), ((leftline), height + 25), (255,100,0), 2, 8, 0)
                cv2.line(blur_image, ((rightline), height - 25), ((rightline), height + 25), (255,100,0), 2, 8, 0)
                cv2.line(blur_image, ((midline), height - 50), ((midline), height + 50), (255,100,0), 2, 8, 0)

                # Prints what direction the car should go
                output = "Straight"
                if(midline > 470 and midline < 490): output = "Straight"
                if(midline > 489 and midline < 510): output = "Slight Right"
                if(midline > 509): output = "Right"
                if(midline < 471 and midline > 450): output = "Slight Left"
                if(midline < 451): output = "Left"
                print(output)

                # Stack source image with lane image and display
                display = np.hstack((image, blur_image))
                display = cv2.resize(display, (1080,500))
                cv2.imshow("Lane Detection", display)
                cv2.waitKey(50)

            except cv2.error as e:
                print("Couldnt load next image: %s" % (e))
                exit()
        else:
            print("----------unable to open cap. incoming crash----------------")

            exit()

if __name__ == "__main__":
    main()
