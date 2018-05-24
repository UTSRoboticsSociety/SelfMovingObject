
import cv2
import numpy as np
import imutils
import Camera
import LaneDetector
import ColorPicker
import Serial2
import serial
import time
import pygame
def main():

    pygame.init()
    screen = pygame.display.set_mode((300,300))
    pygame.display.set_caption('wasd car control')
    camera = None
    detector = None
    color_Picker = None
    enable_Color_Picker = False
    color_Picker_Type = "HSV_Picker"
    work_image = None
    complete_mask_image = None
    direction_line_image = None
    detector_type = "HSVDetector"
    video_resize_width = 1080

    blue_upper = []
    yellow_upper = []
    object_upper = []

    blue_lower = []
    yellow_lower = []
    object_lower = []

    videonumber = 1
    url = ('Videos/video' + str(videonumber) + '.mp4')

    camera = Camera.Camera(video_source = 0)

    seri = Serial2.Serial2('/dev/ttyACM0',9600,8,serial.PARITY_NONE,1,2,False,True,2,False,None)

    camera.open_video()

    work_image = camera.get_frame()

    if color_Picker_Type is "BGR_Picker":
        detector_type = "RGBDetector"

    if color_Picker_Type is "HSV_Picker":
        detector_type = "HSVDetector"

    detector_manager = LaneDetector.lane_detector_manager(detector_type = detector_type)

    detector = detector_manager.get_detector()





    if enable_Color_Picker:
        color_manager = ColorPicker.color_picker_manager(color_type = color_Picker_Type)
        color_picker = color_manager.get_detector()

        blue_upper, blue_lower = color_picker.select_color(image = None, message = "pick blue lane")
        yellow_upper, yellow_lower = color_picker.select_color(image = None, message = "pick yellow lane")
        object_upper, object_lower = color_picker.select_color(image = None, message = "pick object")

        detector.set_colors(blue_upper,yellow_upper,object_upper,
                            blue_lower,yellow_lower,object_lower)

    print("INITIALIZED")
    while camera.playing():
    #while(True):

        start_time = time.time()
        up = False
        down = False
        left = False
        right = False
        pressed = pygame.key.get_pressed()
        # for event in pygame.event.get():

        #print(event)
        if (pressed[pygame.K_w]):
            up = True
            print("W")
        if (pressed[pygame.K_s]): down = True
        if (pressed[pygame.K_a]): left = True
        if (pressed[pygame.K_d]): right = True
        pygame.event.pump()

        while camera.get_frame() is None:  #Comment this block in
            continue

        work_image = camera.get_resize_image(width_size = video_resize_width)
        cropped_image = camera.crop_border_image(image = work_image)

        complete_mask = detector.get_lanes(base_frame = work_image,
                                           cropped_frame = cropped_image)
        if complete_mask is not None:
             direction_line_image, value = detector.draw_direction_lines(mask_image = complete_mask)
        #Send a value to the arduino fofr the servo angle
        value = str((int ((value - 320) / 2)) + 90)
        #value ="90"
        speed = 1410

        control = True
        if(control):
            if(up): speed = 1400
            elif(down): speed = 1600
            else: speed = 1500
            if(left): value = "50"
            elif (right): value = "130"
            else: value = "90"


        #speed = 1500
        message =  "{\"sensor\":\"gps\",\"time\":1351824120,\"data\":[" + str(speed) + "," + value + "]}";
        seri.sendMessage(message,11)


        # Stack source image with lane image and display
        display = np.hstack((work_image, direction_line_image))   #######
        #display = cv2.resize(display, (1080,500))
        display = cv2.resize(display, (1500, 750))                  ########
        cv2.imshow("Lane Detection", display)
        if cv2.waitKey(1) & 0xFF == ord('q'):                       ######
            break                                                       ######
        print("FPS: ", 1.0 / (time.time() - start_time))

### PYTHON MAIN CALL
if __name__ == "__main__":
    main()
