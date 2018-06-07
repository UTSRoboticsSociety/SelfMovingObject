import pygame
import cv2
import numpy as np
import imutils

# Links for Future Use####
# http://www.thorpy.org/tutorials/include.html
# https://www.pygame.org/docs/
# https://www.reddit.com/r/pygame/comments/89ygm7/pygame_awesome_libraries/


class interface(object):
    def __init__(self):
        self.forward = False
        self.backward = False
        self.left = False
        self.right = False
        self.enable_control = False

        self.joystick = None
        self.joystick_name = None
        self.joystick_present = False
        self.axis0 = None
        self.axis1 = None
        self.axis2 = None
        self.axis3 = None
        self.axis4 = None
        self.axis5 = None

        self.pressed = None

        self.screen = None
        self.frame = None
        self.screen_width = 1280
        self.screen_height = 720
        self.menu_size = 280
        self.frame_width = self.screen_width - self.menu_size
        self.screen_caption = "wasd car control"

        pygame.init()
        pygame.joystick.init()

        self.joystick_count = pygame.joystick.get_count()

    def update_frame(self, cv_image):
        cv_image = imutils.resize(cv_image, width=min(self.frame_width,
                                                      cv_image.shape[1]))
        self.frame = cv2.cvtColor(cv_image, cv2.COLOR_BGR2RGB)
        self.frame = np.rot90(self.frame)
        self.frame = pygame.surfarray.make_surface(self.frame)
        self.screen.blit(self.frame, (0, 0))
        pygame.display.update()

    def process_events(self):
        pygame.event.pump()

    def start_screen(self):
        self.screen = pygame.display.set_mode(
            [self.screen_width, self.screen_height])
        pygame.display.set_caption(self.screen_caption)

    def init_joystick(self):
        self.joystick_count = pygame.joystick.get_count()
        if self.joystick_count is not 0:
            self.joystick_present = True
            self.joystick = [pygame.joystick.Joystick(x) for x in
                             range(self.joystick_count)]
            for x in range(self.joystick_count):
                self.joystick[x].init()
                self.joystick_name[x] = self.joystick[x].get_name()
        else:
            print("No Joystick Present")
            self.joystick_present = False

    def get_key_input(self):
        self.pressed = pygame.key.get_pressed()

        if (self.pressed[pygame.K_w]):
            self.forward = True
        elif (self.pressed[pygame.K_s]):
            self.backward = True

        if (self.pressed[pygame.K_a]):
            self.left = True
        elif (self.pressed[pygame.K_d]):
            self.right = True

        if (self.pressed[pygame.K_p]):
            self.enable_control = False
        elif (self.pressed[pygame.K_c]):
            self.enable_control = True

        return (self.forward, self.backward,
                self.left, self.right,
                self.enable_control)

    def get_joystick_count(self):
        self.joystick_count = pygame.joystick.get_count()
        return self.joystick_count

    def check_joystick(self):
        return self.joystick_present

    def get_joystick_input(self, joystick_num):
        if self.joystick_present:
            # Left / Right on left joystick
            self.axis0 = self.joystick[joystick_num].get_axis(0)
            # Up / Dpwn on left joystick
            self.axis1 = self.joystick[joystick_num].get_axis(1)
            # l2 -1 -> 1 #
            # R2 / L2 L2 is positive, R2 is negative.
            self.axis2 = self.joystick[joystick_num].get_axis(2)

            self.axis3 = self.joystick[joystick_num].get_axis(3)

            self.axis4 = self.joystick[joystick_num].get_axis(4)

            # R2  -1 -> 1
            # ####/ L2 L2 is positive, R2 is negative.
            self.axis5 = self.joystick[joystick_num].get_axis(5)

            return(self.axis0,
                   self.axis1,
                   self.axis2,
                   self.axis3,
                   self.axis4,
                   self.axis5)
