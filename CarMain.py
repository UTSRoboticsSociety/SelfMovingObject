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


def initialize():
    blue_upper = []
    yellow_upper = []
    object_upper = []
    finish_upper = []

    blue_lower = []
    yellow_lower = []
    object_lower = []
    finish_lower = []
    detector_type = "HSVDetector"
    enable_Color_Picker = False
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
    serial_usingSerial = True
    camera = WebcamVideoStream(src=0).start()
    # camera = WebcamVideoStream(src="C:\\Users\\Lordbordem.lordbordem-PC\\Desktop\\Robosoc\\SelfMovingObject\\Videos\\video2.mp4").start()

    seri = Serial2.Serial2(port=serial_port,
                           baud=serial_baud_rate,
                           bytesize=serial_byte_size,
                           parity=serial.PARITY_NONE,
                           stopbits=serial_stop_bits,
                           timeout=serial_time_out,
                           xonxoff=serial_xxonxoff,
                           rtscts=serial_rtscts,
                           writetimeout=serial_write_timeout,
                           dstdtr=serial_dstdtr,
                           intercharttimeout=serial_intercharttimeout,
                           usingSerial=serial_usingSerial)

    # camera.open_video()

    # work_image = camera.get_frame()
    work_image = camera.read()

    detector_manager = LaneDetector.lane_detector_manager(
                                    detector_type=detector_type)

    detector = detector_manager.get_detector()

    set_colour_picker(enable_Color_Picker=enable_Color_Picker,
                      detector=detector,
                      detector_type=detector_type)

    main_interface = interface.interface()
    main_interface.start_screen()
    main_interface.init_joystick()
    joystick_count = main_interface.get_joystick_count()

    (blue_upper,
     yellow_upper,
     object_upper,
     blue_lower,
     yellow_lower,
     object_lower,
     finish_upper,
     finish_lower,
     canny_low,
     canny_high) = detector.return_current_colors()

    main_interface.define_hsv_colours(blue_upper,
                                      yellow_upper,
                                      object_upper,
                                      blue_lower,
                                      yellow_lower,
                                      object_lower,
                                      finish_upper,
                                      finish_lower,
                                      canny_low,
                                      canny_high)
    main_interface.create_menu()

    return (camera, seri, main_interface, joystick_count, work_image, detector)


def set_colour_picker(enable_Color_Picker, detector, detector_type):
    blue_upper = []
    yellow_upper = []
    object_upper = []

    blue_lower = []
    yellow_lower = []
    object_lower = []
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


def translate_key_controls(control, up, down, left, right, speed, steering, direction):
    if(control):
        if(up):
            speed = 50
            direction = "1"
        elif(down):
            speed = 50
            direction = "2"
        else:
            speed = 0
            direction = "0"
        if(left):
            steering = "45"
        elif (right):
            steering = "135"
        else:
            steering = "90"

    return (speed, steering, direction)


def translate_stick_controls(axis0, axis1, axis2,
                             axis3, axis4, axis5, speed, steering):

    if(abs(axis0) > 0.1):
        steering = str(90 + 40 * axis0)
    if(abs(axis5 + 1) > 0.1):
        speed = 1430 - 20 * (axis5 + 1)
    elif(abs(axis2 + 1) > 0.1):
        speed = 1570 + 20 * (axis2 + 1)

    return (speed, steering)


def user_control_loop(window, joystick_enable, speed, steering, control, direction):
    axis0 = 0  # Left / Right on left joystick
    # axis1 = 0  # Up / Dpwn on left joystick
    axis2 = 0  # R2 / L2 L2 is positive, R2 is negative.
    axis5 = 0
    up = False
    down = False
    left = False
    right = False

    joystick_count = window.get_joystick_count()

    up, down, left, right, control = window.get_key_input()

    if control is True:
        if joystick_count is not 0 and joystick_enable is True:
            (axis0,
             axis1,
             axis2,
             axis3,
             axis4,
             axis5) = window.get_joystick_input(joystick_num=0)
            (speed, steering) = translate_stick_controls(axis0=axis0,
                                                          axis1=axis1,
                                                          axis2=axis2,
                                                          axis3=axis3,
                                                          axis4=axis4,
                                                          axis5=axis5,
                                                          speed=speed,
                                                          steering=steering)

        elif joystick_count is 0 or joystick_enable is False:
            (speed,
             steering,
             direction) = translate_key_controls(control=control,
                                                 up=up,
                                                 down=down,
                                                 left=left,
                                                 right=right,
                                                 speed=speed,
                                                 steering=steering,
                                                 direction=direction)

    return (speed, steering, control, direction)


def main():
    HSV_Blue_Upper = None
    HSV_Yellow_Upper = None
    HSV_Object_Upper = None
    HSV_Blue_Lower = None
    HSV_Yellow_Lower = None
    HSV_Object_Lower = None
    HSV_Finish_Upper = None
    HSV_Finish_Lower = None

    joystick_enable = False
    control = False
    direction = "0";
    # buttonA = 0 # A Button
    # buttonY = 0 # Y Button
    main_interface = None
    camera = None
    detector = None
    work_image = None
    # complete_mask_image = None
    direction_line_image = None
    # video_resize_width = 1080
    blank_image_count = 0

    # Detector Variables
    detector_lane_height = 250

    foundGreen = False
    greenCount = 0;

    # Detector Lines
    linecount = 3
    leftlines = [0] * linecount
    rightlines = [0] * linecount
    # videonumber = 1
    # url = ('Videos/video' + str(videonumber) + '.mp4')

    # camera = Camera.Camera(video_source = 0)

    (camera,
     seri,
     main_interface,
     joystick_count,
     work_image,
     detector) = initialize()

    print("Initializing..")

    while True:

        start_time = time.time()

        work_image = camera.read()

        if work_image is None:
            blank_image_count += 1
            if blank_image_count is 60:
                break
            continue

        (blueimg,
         yellowimg,
         obstacleimg) = detector.get_lanes(base_frame=work_image,
                                           cropped_frame=work_image.copy())

        obstacle_check = main_interface.get_obstacle_detect()

        for i in range(linecount):
            leftlines[i], rightlines[i] = detector.draw_direction_lines(
                                                h1=detector_lane_height - i*50,
                                                obstacle_enable=obstacle_check)

        (direction_line_image,
         steering,
         canny_edge_image,
         colour_image,
         detected) = detector.mid_line_calc(
                                            detector_lane_height,
                                            leftlines,
                                            rightlines)


        blueimg = cv2.cvtColor(blueimg, cv2.COLOR_GRAY2BGR)
        yellowimg = cv2.cvtColor(yellowimg, cv2.COLOR_GRAY2BGR)
        obstacleimg = cv2.cvtColor(obstacleimg, cv2.COLOR_GRAY2BGR)

        blueimg = cv2.bitwise_and(blueimg, work_image)
        yellowimg = cv2.bitwise_and(yellowimg, work_image)
        # obstacleimg = cv2.bitwise_and(obstacleimg, work_image)

        canny_edge_image = cv2.cvtColor(canny_edge_image, cv2.COLOR_GRAY2BGR)

        if(detected):
            foundGreen = True

        steering = str((int((steering - 320) / 1.8)) + 90)
        speed = 57 - int(abs(int(steering) - 90) / 2.4)
        if(speed < 50):
            speed = 50
        if(foundGreen):
            greenCount = greenCount + 1;
        if(greenCount > 15):
            speed = 0;
        if(greenCount > 30):
            steering = "90"

        if(greenCount > 200):
            greenCount = 0
            foundGreen = False
        direction = "1"
        (speed,
         steering,
         control,
         direction) = user_control_loop(window=main_interface,
                                        joystick_enable=joystick_enable,
                                        speed=speed,
                                        steering=steering,
                                        control=control,
                                        direction=direction)

        if main_interface.get_all_stop():
            mode = "Drive"
            speed = 0
            direction = "0"
            steering = "180"
            message = ("{\"Mode\" : \"" + mode + "\"," +
                       "\"Throttle\" : \"" + str(speed) + "\"," +
                       "\"Direction\" : \"" + direction + "\"," +
                       "\"Steering\" : \"" + steering + "\"}")
        else:
            mode = "Drive"
            # speed = 50
            # direction = "1"
            # steering = "180"
            message = ("{\"Mode\" : \"Drive\","
                       "\"Throttle\" : \"" + str(speed) + "\"," +
                       "\"Direction\" : \"" + direction + "\"," +
                       "\"Steering\" : \"" + steering + "\"}")

        seri.sendMessage(message=message, length=len(message))
        # display = work_image
############################################################################################################
        debug = False
        #debug = True
        if(debug):
            displaytop = np.hstack((obstacleimg, yellowimg, blueimg))
            displaybot = np.hstack((
                          direction_line_image, canny_edge_image, work_image))
            display = np.vstack((displaytop, displaybot))
        else:
            display = direction_line_image
        # display = cv2.resize(display, (1500, 750))

        main_interface.update_frame(display)

        if main_interface.color_update_ready_call():
            (HSV_Blue_Upper,
             HSV_Yellow_Upper,
             HSV_Object_Upper,
             HSV_Blue_Lower,
             HSV_Yellow_Lower,
             HSV_Object_Lower,
             HSV_Finish_Upper,
             HSV_Finish_Lower,
             Upper_Canny_Value,
             Lower_Canny_Value) = main_interface.get_slider_values()

            detector.set_colors(
                           HSV_Blue_Upper, HSV_Yellow_Upper, HSV_Object_Upper,
                           HSV_Blue_Lower, HSV_Yellow_Lower, HSV_Object_Lower,
                           HSV_Finish_Upper, HSV_Finish_Lower,
                           Upper_Canny_Value, Lower_Canny_Value)

        if main_interface.exit_check():
            speed = 0
            steering = "180"
            message = ("{\"Mode\" : \"Drive\"," +
                       "\"Throttle\" : \"" + str(speed) + "\"," +
                       "\"Direction\" : \"0\"," +
                       "\"Steering\" : \"" + str(steering) + "\"}")
            seri.sendMessage(message=message, length=len(message))
            exit()

        print("FPS: ", 1.0 / (time.time() - start_time))

        main_interface.process_events()


# PYTHON MAIN CALL
if __name__ == "__main__":
    main()
