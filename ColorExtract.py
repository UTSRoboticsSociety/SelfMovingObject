import pyautogui, sys
import cv2

# x and y offset from the top right corner of the screen
# to the top right corner of the displayed test_screenshot
# x and y coordinates of the both corner can obtain by running the program
x_offset = 0
y_offset = 94 #94 with thing

# The function is operate by capture and display a screenshot when the program is ran
# As the mouse move through displayed screenshot window HSV and BGR value are displayed in terminal
# The x and y coordinate need to be calibrate to the window, its currently calibrated to unbuntu with menu on the right hand side
def color_extract():
    try:
        #Image is captured and displayed
        image1 = pyautogui.screenshot('test_screenshot.jpg')
        img = cv2.imread('test_screenshot.jpg')
        cv2.imshow('image', img)
        # Convert image to HSV color space
        img_hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
        # Continuously obtain x and y coordinate and access image pixel
        while True:
            cv2.waitKey(10)
            # Get mouse X and Y coordinates
            x, y = pyautogui.position()
            x = x - x_offset
            y = y - y_offset
            if (x > 0 and y > 0):
                #image is accessed by [row,colum]
                blue, green, red = img[y,x]
                H, S, V = img_hsv[y,x]
                positionStr = ('X: ' + str(x).rjust(4) + ' Y: ' + str(y).rjust(4) + ' B: ' + str(blue).rjust(4) + ' G: ' + str(green).rjust(4) + ' R: ' + str(red).rjust(4) +
                 ' H: ' + str(H).rjust(4) + ' S: ' + str(S).rjust(4) + ' V: ' + str(V).rjust(4))
                print(positionStr, end='')
                print('\b' * len(positionStr), end='', flush=True)
        # while True:
    except KeyboardInterrupt:
        print("efp")
        cv2.destroyAllWindows()


color_extract()
