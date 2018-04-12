
class ColorPicker(object):
    def __init__(self):
        # initialize the list of reference points and boolean indicating
        # whether cropping is being performed or not
        self.refPt = []
        self.cropping = False
        self.font = cv2.FONT_HERSHEY_SIMPLEX

        # Snapshot
        self.work_image = []

        # Variables
        self.message_x_cord = 100
        self.message_y_cord = 100
        self.message_color = [255, 255, 255]
        self.message_thickness = 2
        self.message_font_scale = 2


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


class BGRPicker(ColorPicker):
    def __init__(self):
        self.BGR_Blue_Upper = 0
        self.BGR_Red_Upper = 0
        self.BGR_Green_Upper = 0

        self.BGR_Blue_Lower = 0
        self.BGR_Red_Lower = 0
        self.BGR_Green_Lower = 0

        self.BGR_Upper = np.array([1, 1, 1])
        self.BGR_Lower = np.array([1, 1, 1])

        self.refPt = [(0, 0)]

        self.base_image = 'model.jpg'

    def select_color(self, image, message):

        # load the image, clone it, and setup the mouse callback function
        self.work_image = cv2.imread(self.base_image)
        if image is not None:
            self.work_image = image

        cv2.putText(self.work_image, message,
                   (self.message_x_cord, self.message_y_cord),
                    self.font, self.message_font_scale, self.message_color, self.message_thickness)
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

                    average_color_per_row = np.average(roi, axis=0)
                    average_color = np.average(average_color_per_row, axis=0)
                    average_color = np.uint8(average_color)
                    # debug print(average_color)
                    cv2.imshow("ROI", roi)

                    self.BGR_Upper = np.array([average_color[0] + self.BGR_Blue_Upper,
                                     average_color[1] + self.BGR_Red_Upper,
                                     average_color[2] + self.BGR_Green_Upper])

                    self.BGR_Lower = np.array([average_color[0] - self.BGR_Blue_Lower,
                                     average_color[1] - self.BGR_Green_Lower,
                                     average_color[2] - self.BGR_Red_Lower])

                    # debug print("HSV UPPER is " + str(hsvUpper))
                    # debug print("HSV Lower is " + str(hsvLower))

            elif key == ord("q"):
                break

        # close all open windows
        cv2.destroyAllWindows()

        return self.BGR_Upper, self.BGR_Lower


class HSVPicker(ColorPicker):
    def __init__(self):
        self.HSV_Upper = [255,185,80]
        self.HSV_Lower = [100,40,4]

        self.HSV_Hue_Upper = 15
        self.HSV_Hue_Lower = 15

        self.HSV_Saturation_Upper = 180
        self.HSV_Saturation_Lower = 20

        self.HSV_Lightness_Value_Upper = 130
        self.HSV_Lightness_Value_Lower = 130

        self.base_image = 'model.jpg'

        self.refPt = [(0, 0)]

        self.HSV_Upper = np.array([1, 1, 1])
        self.HSV_Lower = np.array([1, 1, 1])

    def select_color(self, image, message):

        # load the image, clone it, and setup the mouse callback function

        self.work_image = cv2.imread(self.base_image)
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

                    self.HSV_Upper = np.array([average_color[0] + self.HSV_Hue_Upper,
                                     average_color[1] + self.HSV_Saturation_Upper,
                                     average_color[2] + self.HSV_Lightness_Value_Upper])

                    self.HSV_Lower = np.array([average_color[0] - self.HSV_Hue_Lower,
                                     average_color[1] - self.HSV_Saturation_Lower,
                                     average_color[2] - self.HSV_Lightness_Value_Lower])

                    # debug print("HSV UPPER is " + str(hsvUpper))
                    # debug print("HSV Lower is " + str(hsvLower))

            elif key == ord("q"):
                break

        # close all open windows
        cv2.destroyAllWindows()

        return self.HSV_Upper, self.HSV_Lower


class color_picker_manager(object):
    def __init__(self, color_type):
        self.color_type = color_type
        self.video_name = video_name


    def get_detector(self):
        if self.color_type == "BGR_Picker":
            return BGRPicker()

        if self.color_type == "HSV_Picker":
            return HSVPicker()

        else:
            raise NotImplementedError()
