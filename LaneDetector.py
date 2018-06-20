import cv2
import numpy as np
import imutils


class LaneDetector(object):
    def __init__(self):
        self.work_frame = None
        self.cropped_work_frame = None

        self.canny_edge_image = None
        self.colour_image = None

        self.blue_lane_mask = None
        self.yellow_lane_mask = None
        self.object_mask = None
        self.obstacle_mask = None
        self.blue_line_mask = None
        self.yellow_line_mask = None

        self.both_lane_mask = None
        self.lane_object_mask = None
        self.complete_mask = None
        self.overlay_mask = None

        self.HSV_Blue_Upper = None
        self.HSV_Yellow_Upper = None
        self.HSV_Object_Upper = None
        self.HSV_Blue_Lower = None
        self.HSV_Yellow_Lower = None
        self.HSV_Object_Lower = None
        self.HSV_Finish_Upper = None
        self.HSV_Finish_Lower = None

        self.BGR_Blue_Upper = None
        self.BGR_Yellow_Upper = None
        self.BGR_Object_Upper = None
        self.BGR_Blue_Lower = None
        self.BGR_Yellow_Lower = None
        self.BGR_Object_Lower = None
        self.BGR_Finish_Upper = None
        self.BGR_Finish_Lower = None

        self.object_center_x = 0
        self.object_center_y = 0

        # Lane Detect Modifieres (Two Green Lines)
        self.lane_height = 330
        self.lane_width = 300
        self.lane_screen_size_multiplier = 640
        self.lane_cross_over_color = [0, 255, 0]
        self.lane_direction_line_color = [255, 100, 0]
        self.lane_line_thickness = 2
        self.lane_line_type = 8
        self.lane_line_shift = 0

        self.border_size = 330
        self.border_x_limit = 960
        self.border_y_limit = 720
        self.border_color = [0, 0, 0]

        self.kernel_size = 5

        self.travel_straight_right_limit = 470
        self.travel_straight_left_limit = 490

        self.travel_slight_right_right_limit = 489
        self.travel_slight_right_left_limit = 510

        self.travel_slight_left_right_limit = 471
        self.travel_slight_left_left_limit = 450

        self.travel_left__limit = 451

        self.travel_right_limit = 509

        self.work_mask = None
        self.gray_image = None
        self.blur_image = None
        self.display_image = None

        self.edge_low_threshold = 0
        self.edge_high_threshold = 0

        self.colour_output = True

        # Direction lines
        self.travel_direction = 0
        self.mid_line = 0

        # initial positions of detection lines
        self.lv = int(self.lane_width / 2)
        self.rv = int(self.lane_width / 2)

    # returns center over the lane detecting lines
    def laneDetect(self, pixel_threshold, width):

        pixel_threshold = pixel_threshold.flatten()
        value = 0
        count = 0

        for i in range(width):
            if (pixel_threshold[i] > 0):
                value = value + 1 * i
                count = count + 1
        if(count > 0):
            value = (int)(value / count)
        return value

    def objectDetect(self, pixel_threshold, width, height):  # Not Used

        pixel_threshold = pixel_threshold.flatten()
        value = 0
        rise = 0
        count = 0
        for x in range(height):
            for i in range(width):
                if (pixel_threshold[i] > 0):
                    value = value + 1 * i
                    rise = rise + 1 * x
                    count = count + 1
        if(count > 0):
            value = (int)(value / count)
            rise = (int)(rise / count)
        print(value, rise)
        return value, rise

    def obstacleDetection(self):
        obstacle = self.obstacle_mask[100:380, 0:640]
        obstacle = cv2.GaussianBlur(obstacle, (5, 5), 0)
        obstacle = cv2.threshold(obstacle, 60, 255, cv2.THRESH_BINARY)[1]
        cnts = cv2.findContours(obstacle, cv2.RETR_EXTERNAL,
                                cv2.CHAIN_APPROX_SIMPLE)
        cnts = cnts[0] if imutils.is_cv2() else cnts[1]
        count = 0
        tX = 0
        tY = 0
        for c in cnts:
            # compute the center of the contour
            M = cv2.moments(c)
            cX = int(M["m10"] / M["m00"])
            cY = int(M["m01"] / M["m00"])
            tX = tX + cX
            tY = tY + cY
            count = count + 1
            # draw the contour and center of the shape on the image
        if(count > 0):
            tX = int(tX / count)
            tY = int(tY / count)

        return (tX, tY)

    def draw_direction_lines(self, h1=None, h2=None, h3=None):

        self.lane_height = h1

        self.lane_screen_size_multiplier = self.complete_mask.shape[1]
        # blur_image = self.get_blur_image(self.complete_mask) #why?
        self.overlay_mask = self.complete_mask
        lx1 = 0  # ~ lx1 is is left x coord of the first line
        rx1 = lx1 + self.lane_width
        lx2 = self.lane_screen_size_multiplier - rx1
        rx2 = self.lane_screen_size_multiplier - lx1

        # grabs thin line of pixels for lane detection
        # blue_image = cv2.cvtColor(self.blue_lane_mask, cv2.COLOR_GRAY2BGR)
        # yellow_image =cv2.cvtColor(self.yellow_lane_mask, cv2.COLOR_GRAY2BGR)
        # leftPixels =
        # cv2.cvtColor(blue_image[self.lane_height:self.lane_height + 1,
        # lx1:rx1], cv2.COLOR_BGR2GRAY)
        # rightPixels =
        # cv2.cvtColor(yellow_image[self.lane_height:self.lane_height + 1,
        # lx2:rx2], cv2.COLOR_BGR2GRAY)

        self.travel_direction = 0
        if(self.travel_direction is 0):
            leftPixels = self.blue_line_mask[self.lane_height:
                                             self.lane_height+1, lx1:rx1]
            rightPixels = self.yellow_line_mask[self.lane_height:
                                                self.lane_height+1, lx2:rx2]
        if(self.travel_direction is 1):
            rightPixels = self.blue_line_mask[self.lane_height:
                                              self.lane_height+1, lx2:rx2]
            leftPixels = self.yellow_line_mask[self.lane_height:
                                               self.lane_height+1, lx1:rx1]

        if(self.laneDetect(pixel_threshold=leftPixels,
                           width=self.lane_width) > 0
           or self.lv is None):
            self.lv = self.laneDetect(pixel_threshold=leftPixels,
                                      width=self.lane_width)

        if(self.laneDetect(pixel_threshold=rightPixels,
                           width=self.lane_width) > 0
           or self.rv is None):
            self.rv = self.laneDetect(pixel_threshold=rightPixels,
                                      width=self.lane_width)

        # objectPixels =
        # self.test_mask[self.lane_height - 300:self.lane_height + 1,
        # 0:self.test_mask.shape[1]]
        # self.object_center_x, self.object_center_y =
        # self.objectDetect(pixel_threshold = objectPixels,
        # width = self.test_mask.shape[1], height =300)
        # if(self.object_center_x > 0):
        #     print("OBJECTDETECTED")

        (tX, tY) = self.obstacleDetection()

        # Draw lines over the image for lane detection
        leftline = lx1 + self.lv
        rightline = lx2 + self.rv  # int(self.lane_width / 2)#+ self.rv
        if(tX > 0):
            if(abs(tX - leftline) > abs(tX - rightline)):
                rightline = tX
            else:
                leftline = tX

        self.mid_line = (int)((rightline + leftline) / 2)
        cv2.line(self.overlay_mask, (lx1, self.lane_height),
                 (rx1, self.lane_height),
                 self.lane_cross_over_color, self.lane_line_thickness,
                 self.lane_line_type, self.lane_line_shift)

        cv2.line(self.overlay_mask, (lx2, self.lane_height),
                 (rx2, self.lane_height),
                 self.lane_cross_over_color, self.lane_line_thickness,
                 self.lane_line_type, self.lane_line_shift)

        cv2.line(self.overlay_mask, ((leftline), self.lane_height - 25),
                 ((leftline), self.lane_height + 25),
                 self.lane_direction_line_color,
                 self.lane_line_thickness,
                 self.lane_line_type, self.lane_line_shift)

        cv2.line(self.overlay_mask, ((rightline), self.lane_height - 25),
                 ((rightline), self.lane_height + 25),
                 self.lane_direction_line_color,
                 self.lane_line_thickness,
                 self.lane_line_type, self.lane_line_shift)

        cv2.line(self.overlay_mask, ((self.mid_line), self.lane_height - 50),
                 ((self.mid_line), self.lane_height + 50),
                 self.lane_direction_line_color,
                 self.lane_line_thickness,
                 self.lane_line_type, self.lane_line_shift)

        if(tX > 0):
            cv2.circle(self.overlay_mask, (tX, tY + 100),
                       7, (0, 0, 255), thickness=10, lineType=8, shift=0)

        # cv2.cvtColor(self.test_mask, cv2.COLOR_GRAY2BGR) #self.colour_image
        return (self.overlay_mask, self.mid_line,
                self.canny_edge_image, self.colour_image)

    def edge_detection(self, mask_image):
        # Basic Edge Detection (not implemented)
        # blur_image =
        # cv2.cvtColor(mask_image, cv2.COLOR_BGR2GRAY)
        # self.blur_image(mask_image)
        self.edge_low_threshold = 10
        self.edge_high_threshold = 50
        self.canny_edge_image = cv2.Canny(cv2.cvtColor(mask_image,
                                                       cv2.COLOR_BGR2GRAY),
                                          self.edge_low_threshold,
                                          self.edge_high_threshold)
        # self.canny_edge_image =
        # cv2.cvtColor(self.canny_edge_image, cv2.COLOR_GRAY2BGR)
        # return self.canny_edge_image

    def get_blur_image(self, base_image):
        self.work_mask = base_image.copy()
        self.blur_image = cv2.GaussianBlur(self.work_mask,
                                           (self.kernel_size,
                                            self.kernel_size), 0)
        return self.blur_image

    def return_current_colors(self):
        raise NotImplementedError

    def load_default_color_values(self):
        raise NotImplementedError

    def finish_line(self):
        raise NotImplementedError


class HSVDetector(LaneDetector):
    def __init__(self):
        super(HSVDetector, self).__init__
        LaneDetector.__init__(self)
        self.load_default_color_values()

    def return_current_colors(self):
        return (self.HSV_Blue_Upper,
                self.HSV_Yellow_Upper,
                self.HSV_Object_Upper,
                self.HSV_Blue_Lower,
                self.HSV_Yellow_Lower,
                self.HSV_Object_Lower,
                self.HSV_Finish_Upper,
                self.HSV_Finish_Lower)

    def set_colors(self,
                   HSV_Blue_Upper, HSV_Yellow_Upper, HSV_Object_Upper,
                   HSV_Blue_Lower, HSV_Yellow_Lower, HSV_Object_Lower,
                   HSV_Finish_Upper, HSV_Finish_Lower):

        if HSV_Blue_Upper is not None:
            self.HSV_Blue_Upper = np.array(HSV_Blue_Upper, dtype="uint8")
        if HSV_Yellow_Upper is not None:
            self.HSV_Yellow_Upper = np.array(HSV_Yellow_Upper, dtype="uint8")
        if HSV_Object_Upper is not None:
            self.HSV_Object_Upper = np.array(HSV_Object_Upper, dtype="uint8")

        if HSV_Blue_Lower is not None:
            self.HSV_Blue_Lower = np.array(HSV_Blue_Lower, dtype="uint8")
        if HSV_Yellow_Lower is not None:
            self.HSV_Yellow_Lower = np.array(HSV_Yellow_Lower, dtype="uint8")
        if HSV_Object_Lower is not None:
            self.HSV_Object_Lower = np.array(HSV_Object_Lower, dtype="uint8")

        if HSV_Finish_Upper is not None:
            self.HSV_Finish_Upper = np.array(HSV_Finish_Upper, dtype="uint8")
        if HSV_Finish_Lower is not None:
            self.HSV_Finish_Lower = np.array(HSV_Finish_Lower, dtype="uint8")

    def load_default_color_values(self):
        # 0 orange, 10 orange, 20 orangeyellow,
        # 30 yellow green, 40 yellow BGR_Green_Lower

        # 50 green, 60 blue?, 70 teal green,
        # 80 teal blue, 90 blues, 100 deep blues,
        # 110 deeper blues #120 purlply #130 purply, #140 pink #150 pink # 160
        # 170 - 180 red

        self.HSV_Blue_Upper = np.array([130, 255, 255], dtype="uint8")
        self.HSV_Blue_Lower = np.array([80, 20, 20], dtype="uint8")
    #    self.HSV_Blue_Lower =  np.array([255,255,255], dtype = "uint8")

        self.HSV_Yellow_Upper = np.array([40, 255, 255], dtype="uint8")
        self.HSV_Yellow_Lower = np.array([15, 0, 50], dtype="uint8")

        # self.HSV_Yellow_Upper = np.array([0,0,0], dtype = "uint8")
        # self.HSV_Yellow_Lower =  np.array([0,0,0], dtype = "uint8")

        self.HSV_Object_Upper = np.array([180, 255, 255], dtype="uint8")
        self.HSV_Object_Lower = np.array([160, 100, 20], dtype="uint8")

        self.HSV_Finish_Upper = np.array([180, 255, 255], dtype="uint8")
        self.HSV_Finish_Lower = np.array([160, 100, 20], dtype="uint8")

    def get_lanes(self, base_frame, cropped_frame):
        # HSV_Blue_Upper = self.HSV_Blue_Upper,
        # HSV_Yellow_Upper = self.HSV_Yellow_Upper,
        # HSV_Object_Upper = self.HSV_Object_Upper,
        # HSV_Blue_Lower  = self.HSV_Blue_Lower,
        # HSV_Yellow_Lower = self.HSV_Yellow_Lower,
        # HSV_Object_Lower  = self.HSV_Object_Lower,):

        self.edge_detection(base_frame)
        # cv2.imshow("edges", self.edge_detection(base_frame))
        # cv2.imshow("edges", self.canny_edge_image)
        # cv2.waitKey(1)

        self.work_frame = base_frame.copy()
        self.cropped_work_frame = cropped_frame.copy()
        self.gray_image = cv2.cvtColor(self.cropped_work_frame,
                                       cv2.COLOR_BGR2GRAY)

        self.blue_lane_mask = self.mask_colors(self.work_frame,
                                               self.HSV_Blue_Upper,
                                               self.HSV_Blue_Lower)
        self.yellow_lane_mask = self.mask_colors(self.work_frame,
                                                 self.HSV_Yellow_Upper,
                                                 self.HSV_Yellow_Lower)
        self.object_mask = self.mask_colors(self.work_frame,
                                            self.HSV_Object_Upper,
                                            self.HSV_Object_Lower)

        self.obstacle_mask = self.object_mask.copy()
        self.lane_object_mask = cv2.bitwise_or(self.blue_lane_mask,
                                               self.yellow_lane_mask,
                                               self.object_mask)
        self.colour_image = cv2.cvtColor(self.lane_object_mask,
                                         cv2.COLOR_GRAY2BGR)
        self.colour_image = cv2.bitwise_and(self.work_frame, self.colour_image)

        self.lane_object_mask = cv2.bitwise_and(self.object_mask,
                                                self.canny_edge_image)

        self.blue_line_mask = cv2.bitwise_and(self.blue_lane_mask,
                                              self.canny_edge_image)
        self.yellow_line_mask = cv2.bitwise_and(self.yellow_lane_mask,
                                                self.canny_edge_image)

        self.colour_output = True

        if(self.colour_output):
            self.lane_object_mask = cv2.cvtColor(self.lane_object_mask,
                                                 cv2.COLOR_GRAY2BGR)

            # Check if AND distorts colour
            self.complete_mask = cv2.bitwise_and(self.work_frame,
                                                 self.lane_object_mask)

        else:
            self.complete_mask = cv2.bitwise_and(self.gray_image,
                                                 self.lane_object_mask)
            self.complete_mask = cv2.cvtColor(self.complete_mask,
                                              cv2.COLOR_GRAY2BGR)

        return self.complete_mask

    def mask_colors(self, frame, hsvUpper, hsvLower):
        # blurred = cv2.GaussianBlur(dst, (5, 5), 0)
        # thresh = cv2.threshold(blurred, 60, 255, cv2.THRESH_BINARY)[1]
        self.work_frame = frame.copy()

        hsv = cv2.cvtColor(self.work_frame, cv2.COLOR_BGR2HSV)

        # hsv = cv2.bilateralFilter(hsv,9,75,75)

        # Debug - Show HSV converted image
        # cv2.imshow('Thresh', hsv)

        # construct a mask for the color "green", then perform
        # a series of dilations and erosions to remove any small
        # blobs left in the mask
        self.work_mask = cv2.inRange(hsv, hsvLower, hsvUpper)
        self.work_mask = cv2.erode(self.work_mask, None, iterations=2)
        self.work_mask = cv2.dilate(self.work_mask, None, iterations=2)
        # Debug - Show Masked Image
        # cv2.imshow('Mask', mask)

        return self.work_mask


class BGRDetector(LaneDetector):
    def __init__(self):
        super(BGRDetector, self).__init__
        LaneDetector.__init__(self)
        self.load_default_color_values()

    def return_current_colors(self):
        return (self.BGR_Blue_Upper,
                self.BGR_Yellow_Upper,
                self.BGR_Object_Upper,
                self.BGR_Blue_Lower,
                self.BGR_Yellow_Lower,
                self.BGR_Object_Lower)

    def load_default_color_values(self):
        self.BGR_Blue_Upper = np.array([255, 100, 130], dtype="uint8")
        self.BGR_Blue_Lower = np.array([100, 0, 0], dtype="uint8")

        self.BGR_Yellow_Upper = np.array([200, 230, 235], dtype="uint8")
        self.BGR_Yellow_Lower = np.array([100, 150, 150], dtype="uint8")

        self.BGR_Object_Upper = np.array([0, 0, 0], dtype="uint8")
        self.BGR_Object_Lower = np.array([0, 0, 4], dtype="uint8")

        # no 193 193 193

    def set_colors(self,
                   BGR_Blue_Upper, BGR_Yellow_Upper, BGR_Object_Upper,
                   BGR_Blue_Lower, BGR_Yellow_Lower, BGR_Object_Lower):

        if BGR_Blue_Upper is not None:
            self.BGR_Blue_Upper = np.array(BGR_Blue_Upper, dtype="uint8")
        if BGR_Yellow_Upper is not None:
            self.BGR_Yellow_Upper = np.array(BGR_Yellow_Upper, dtype="uint8")
        if BGR_Object_Upper is not None:
            self.BGR_Object_Upper = np.array(BGR_Object_Upper, dtype="uint8")

        if BGR_Blue_Lower is not None:
            self.BGR_Blue_Lower = np.array(BGR_Blue_Lower, dtype="uint8")
        if BGR_Yellow_Lower is not None:
            self.BGR_Yellow_Lower = np.array(BGR_Yellow_Lower, dtype="uint8")
        if BGR_Object_Lower is not None:
            self.BGR_Object_Lower = np.array(BGR_Object_Lower, dtype="uint8")

    def mask_colors(self, frame, BGRUpper, BGRLower):
        # blurred = cv2.GaussianBlur(dst, (5, 5), 0)
        # thresh = cv2.threshold(blurred, 60, 255, cv2.THRESH_BINARY)[1]

        # hsv = cv2.bilateralFilter(hsv,9,75,75)

        # Debug - Show HSV converted image
        # cv2.imshow('Thresh', hsv)

        self.work_frame = frame.copy()

        # construct a mask for the color "green", then perform
        # a series of dilations and erosions to remove any small
        # blobs left in the mask
        self.work_mask = cv2.inRange(frame, BGRLower, BGRUpper)
        self.work_mask = cv2.erode(self.work_mask, None, iterations=2)
        self.work_mask = cv2.dilate(self.work_mask, None, iterations=2)
        # Debug - Show Masked Image
        # cv2.imshow('Mask', mask)

        return self.work_mask

    def get_lanes(self, base_frame, cropped_frame):

        self.work_frame = base_frame.copy()
        self.cropped_work_frame = cropped_frame.copy()
        self.gray_image = cv2.cvtColor(self.cropped_work_frame,
                                       cv2.COLOR_BGR2GRAY)

        self.blue_lane_mask = self.mask_colors(self.work_frame,
                                               self.BGR_Blue_Upper,
                                               self.BGR_Blue_Lower)

        self.yellow_lane_mask = self.mask_colors(self.work_frame,
                                                 self.BGR_Yellow_Upper,
                                                 self.BGR_Yellow_Lower)

        self.object_mask = self.mask_colors(self.work_frame,
                                            self.BGR_Object_Upper,
                                            self.BGR_Object_Lower)

        self.both_lane_mask = cv2.bitwise_or(self.blue_lane_mask,
                                             self.yellow_lane_mask)
        self.lane_object_mask = cv2.bitwise_or(self.both_lane_mask,
                                               self.object_mask)

        self.colour_output = True
        if(self.colour_output):
            self.lane_object_mask = cv2.cvtColor(self.lane_object_mask,
                                                 cv2.COLOR_GRAY2BGR)
            self.complete_mask = cv2.bitwise_and(self.work_frame,
                                                 self.lane_object_mask)

        else:
            self.complete_mask = cv2.bitwise_and(self.gray_image,
                                                 self.lane_object_mask)
            self.complete_mask = cv2.cvtColor(self.complete_mask,
                                              cv2.COLOR_GRAY2BGR)

        return self.complete_mask


class lane_detector_manager(object):
    def __init__(self, detector_type):
        self.detector_type = detector_type

    def get_detector(self):
        if self.detector_type == "RGBDetector":
            return BGRDetector()
        if self.detector_type == "HSVDetector":
            return HSVDetector()

        else:
            raise NotImplementedError()
