
import cv2
import numpy as np
# import imutils
# import Camera
import LaneDetector
import ColorPicker
import Serial2
import serial
import time
import interface
from imutils.video import WebcamVideoStream


def main():
    axis0 = 0  # Left / Right on left joystick
    # axis1 = 0  # Up / Dpwn on left joystick
    axis2 = 0  # R2 / L2 L2 is positive, R2 is negative.
    axis5 = 0
    # buttonA = 0 # A Button
    # buttonY = 0 # Y Button
    main_interface = None
    camera = None
    detector = None
    color_picker = None
    enable_Color_Picker = False
    work_image = None
    # complete_mask_image = None
    direction_line_image = None
    detector_type = "HSVDetector"
    # video_resize_width = 1080
    serial_baud_rate = 115200
    serial_port = "/dev/ttyUSB0"
    serial_byte_size = 8
    serial_stop_bits = 1
    serial_time_out = 2
    serial_xxonxoff = False
    serial_rtscts = True
    serial_write_timeout = 2
    serial_dstdtr = False
    serial_intercharttimeout = None

    # Detector Variables
    detector_lane_height = 330

    blue_upper = []
    yellow_upper = []
    object_upper = []

    blue_lower = []
    yellow_lower = []
    object_lower = []

    # videonumber = 1
    # url = ('Videos/video' + str(videonumber) + '.mp4')

    # camera = Camera.Camera(video_source = 0)
    camera = WebcamVideoStream(src=0).start()

    seri = Serial2.Serial2(serial_port,
                           serial_baud_rate, serial_byte_size,
                           serial.PARITY_NONE,
                           serial_stop_bits, serial_time_out,
                           serial_xxonxoff, serial_rtscts,
                           serial_write_timeout,
                           serial_dstdtr, serial_intercharttimeout)

    # camera.open_video()

    main_interface = interface.interface()
    main_interface.start_screen()
    main_interface.init_joystick()
    joystick_count = main_interface.get_joystick_count()

    # work_image = camera.get_frame()
    work_image = camera.read()

    detector_manager = LaneDetector.lane_detector_manager(
                                    detector_type=detector_type)

    detector = detector_manager.get_detector()

    if enable_Color_Picker:
        color_manager = ColorPicker.color_picker_manager(
                                    color_type=detector_type)

        color_picker = color_manager.get_detector()

        (blue_upper,
         blue_lower) = color_picker.select_color(
                                    image=None,
                                    message="pick blue lane")
        (yellow_upper,
         yellow_lower) = color_picker.select_color(image=None,
                                                   message="pick yellow lane")
        (object_upper,
         object_lower) = color_picker.select_color(image=None,
                                                   message="pick object")

        detector.set_colors(blue_upper, yellow_upper, object_upper,
                            blue_lower, yellow_lower, object_lower)

    print("Initializing..")
    control = True

    while True:

        start_time = time.time()
        up = False
        down = False
        left = False
        right = False

        work_image = camera.read()

        if work_image is None:
            continue

        # complete_mask = detector.get_lanes(base_frame=work_image,
        # cropped_frame=work_image.copy())

        (direction_line_image,
         value,
         canny_edge_image,
         colour_image) = detector.draw_direction_lines(h1=detector_lane_height)

        canny_edge_image = cv2.cvtColor(canny_edge_image, cv2.COLOR_GRAY2BGR)
        value = str((int((value - 320) / 2)) + 90)
        speed = 1390 + int(abs(int(value) - 90) / 2)

        joystick_count = main_interface.get_joystick_count()

        up, down, left, right, control = main_interface.get_key_input()

        if joystick_count is not 0:
            (axis0,
             axis1,
             axis2,
             axis3,
             axis4,
             axis5) = main_interface.get_joystick_input(joystick_num=0)

            if(abs(axis0) > 0.1):
                value = str(90 + 40 * axis0)
            if(abs(axis5 + 1) > 0.1):
                speed = 1430 - 20 * (axis5 + 1)
            elif(abs(axis2 + 1) > 0.1):
                speed = 1570 + 20 * (axis2 + 1)

        if(control):
            if(up):
                speed = 1380
            elif(down):
                speed = 1600
            else:
                speed = 1500
            if(left):
                value = "45"
            elif (right):
                value = "135"
            else:
                value = "90"

        message = "{\"data\":["+str(speed)+","+value + "]}"
        seri.sendMessage(message, 11)
        # display = work_image
        displaytop = np.hstack((work_image, direction_line_image))
        displaybot = np.hstack((canny_edge_image, colour_image))
        display = np.vstack((displaytop, displaybot))

        # display = cv2.resize(display, (1500, 750))

        cv2.imshow("Lane Detection", display)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
        print("FPS: ", 1.0 / (time.time() - start_time))

        main_interface.process_events()


# PYTHON MAIN CALL
if __name__ == "__main__":
    main()
