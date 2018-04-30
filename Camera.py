
import cv2
import numpy as np
import imutils

class Camera(object):
    def __init__(self, video_source):
        self.video_source = video_source
        self.image_raw = None
        self.image_resize = None
        self.cropped_image = None
        self.border_size = 0
        self.retval = None
        self.video_feed = None
        self.video_writer = None
        self.detection_video_writer = None
        self.counter = 0
        self.base_location = '/'
        self.frame_rate = 25
        self.frame_height = 0
        self.frame_width = 0

    def set_video_source(self, video_source):
        self.video_source = video_source

    def open_video(self):
        self.video_feed = cv2.VideoCapture(self.video_source)

    def get_frame(self):
        (self.retval, self.image_raw) = self.video_feed.read()
        return self.image_raw

    def get_framecount(self):
        return self.video_feed.get(cv2.CAP_PROP_FRAME_COUNT)

    def get_resize_image(self, width_size = 600):
        self.get_frame()
        if self.image_raw is not None:
            self.image_resize = imutils.resize(self.image_raw,
                                 width=min(width_size, self.image_raw.shape[1]))
        return self.image_resize

    def get_frame_size(self, image):
        self.frame_height, self.frame_width = image.shape[:2]
        return self.frame_height, self.frame_width

    def crop_border_image(self, image):
        height, width = self.get_frame_size(image)
        self.cropped_image = image[self.border_size:height,0:width]
        self.cropped_image = cv2.copyMakeBorder(self.cropped_image,
                                                top = self.border_size, bottom = 0,
                                                left = 0, right = 0,
                                                borderType = cv2.BORDER_CONSTANT,
                                                value = [0,0,0])
        return self.cropped_image

    def release_camera(self):
        self.video_feed.release()

    def get_frame_number(self):
        return self.video_feed.get(cv2.CAP_PROP_POS_FRAMES)

    def playing(self):
        return self.video_feed.isOpened()

    def empty(self):
        return type(self.image_raw) == type(None)

    def write(self, image):
        self.video_writer.write(image)

    def write_detection(self, image):
        self.detection_video_writer.write(image)

    def enable_write(self, output_path, image):
        fourcc = cv2.VideoWriter_fourcc(*'XVID')
        height, width = image.shape[:2]
        self.video_writer = cv2.VideoWriter((self.base_location+output_path), fourcc, self.frame_rate, (width, height))

    def enable_detection_write(self, output_path, image):
        fourcc = cv2.VideoWriter_fourcc(*'XVID')
        height, width = image.shape[:2]
        self.detection_video_writer = cv2.VideoWriter((self.base_location+output_path), fourcc, self.frame_rate, (width, height))

    def close_writer(self):
        self.video_writer.release()

    def close_detection_writer(self):
        self.detection_video_writer.release()
