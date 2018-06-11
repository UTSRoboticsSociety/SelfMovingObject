import pygame
import cv2
import numpy as np
import imutils
import thorpy


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

        self.Blue_Hue_Slider = None
        self.Blue_Saturation_Slider = None
        self.Blue_Value_Slider = None

        self.Yellow_Hue_Slider = None
        self.Yellow_Saturation_Slider = None
        self.Yellow_Value_Slider = None

        self.Object_Hue_Slider = None
        self.Object_Saturation_Slider = None
        self.Object_Value_Slider = None

        self.Finish_Hue_Slider = None
        self.Finish_Saturation_Slider = None
        self.Finish_Value_Slider = None

        self.Blue_Hue_Value = None
        self.Blue_Saturation_Value = None
        self.Blue_Value_Value = None

        self.Yellow_Hue_Value = None
        self.Yellow_Saturation_Value = None
        self.Yellow_Value_Value = None

        self.Object_Hue_Value = None
        self.Object_Saturation_Value = None
        self.Object_Value_Value = None

        self.Finish_Hue_Value = None
        self.Finish_Saturation_Value = None
        self.Finish_Value_Value = None

        self.slide_limit = 255

        self.menu = None
        self.menu_content = None
        self.menu_reaction = None

        self.pressed = None

        self.text = None
        self.text_font_object = None
        self.text_font = 'arial'
        self.display_text = None
        self.text_color = (255, 255, 255)

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

    def create_menu(self):
        self.Blue_Hue_Slider = thorpy.SliderX.make(length=100,
                                                   limvals=(
                                                       0,
                                                       self.slide_limit),
                                                   text="Lane 1 Hue:",
                                                   type_=int)
        self.Blue_Saturation_Slider = thorpy.SliderX.make(length=100,
                                                          limvals=(
                                                             0,
                                                             self.slide_limit),
                                                          text="Lane 1 Sat:",
                                                          type_=int)
        self.Blue_Value_Slider = thorpy.SliderX.make(length=100,
                                                     limvals=(
                                                         0,
                                                         self.slide_limit),
                                                     text="Lane 1 Value:",
                                                     type_=int)

        self.Yellow_Hue_Slider = thorpy.SliderX.make(length=100,
                                                     limvals=(
                                                         0,
                                                         self.slide_limit),
                                                     text="Lane 2 Hue:",
                                                     type_=int)
        self.Yellow_Saturation_Slider = thorpy.SliderX.make(length=100,
                                                            limvals=(
                                                             0,
                                                             self.slide_limit),
                                                            text="Lane 2 Sat:",
                                                            type_=int)
        self.Yellow_Value_Slider = thorpy.SliderX.make(length=100,
                                                       limvals=(
                                                           0,
                                                           self.slide_limit),
                                                       text="Lane 2 Value:",
                                                       type_=int)

        self.Object_Hue_Slider = thorpy.SliderX.make(length=100,
                                                     limvals=(
                                                         0,
                                                         self.slide_limit),
                                                     text="Object Hue:",
                                                     type_=int)
        self.Object_Saturation_Slider = thorpy.SliderX.make(length=100,
                                                            limvals=(
                                                             0,
                                                             self.slide_limit),
                                                            text="Object Sat:",
                                                            type_=int)
        self.Object_Value_Slider = thorpy.SliderX.make(length=100,
                                                       limvals=(
                                                           0,
                                                           self.slide_limit),
                                                       text="Object Value:",
                                                       type_=int)

        self.Finish_Hue_Slider = thorpy.SliderX.make(length=100,
                                                     limvals=(
                                                         0,
                                                         self.slide_limit),
                                                     text="Finish Hue:",
                                                     type_=int)
        self.Finish_Saturation_Slider = thorpy.SliderX.make(length=100,
                                                            limvals=(
                                                             0,
                                                             self.slide_limit),
                                                            text="Finish Sat:",
                                                            type_=int)
        self.Finish_Value_Slider = thorpy.SliderX.make(length=100,
                                                       limvals=(
                                                        0,
                                                        self.slide_limit),
                                                       text="Finish Value:",
                                                       type_=int)
        self.menu_content = thorpy.Box.make(elements=[
            self.Blue_Hue_Slider,
            self.Blue_Saturation_Slider,
            self.Blue_Value_Slider,
            self.Yellow_Hue_Slider,
            self.Yellow_Saturation_Slider,
            self.Yellow_Value_Slider,
            self.Object_Hue_Slider,
            self.Object_Saturation_Slider,
            self.Object_Value_Slider,
            self.Finish_Hue_Slider,
            self.Finish_Saturation_Slider,
            self.Finish_Value_Slider])

        self.menu_reaction = thorpy.Reaction(
            reacts_to=thorpy.constants.THORPY_EVENT,
            reac_func=self.react_slider,
            event_args={"id": thorpy.constants.EVENT_SLIDE},
            reac_name="slider reaction")
        self.menu_content.add_reaction(self.menu_reaction)

        self.menu = thorpy.Menu(self.menu_content)

        for element in self.menu.get_population():
            element.surface = self.screen

        self.menu_content.set_topleft((self.frame_width, 100))
        self.menu_content.blit()
        self.menu_content.update()

    def get_slider_values(self):
        return (
            self.Blue_Hue_Value,
            self.Blue_Saturation_Value,
            self.Blue_Value_Value,

            self.Yellow_Hue_Value,
            self.Yellow_Saturation_Value,
            self.Yellow_Value_Value,

            self.Object_Hue_Value,
            self.Object_Saturation_Value,
            self.Object_Value_Value,

            self.Finish_Hue_Value,
            self.Finish_Saturation_Value,
            self.Finish_Value_Value
        )

    def react_slider(self, event):
        self.Blue_Hue_Value = self.Blue_Hue_Slider.get_value()
        self.Blue_Saturation_Value = self.Blue_Saturation_Value.get_value()
        self.Blue_Value_Value = self.Blue_Value_Value.get_value()

        self.Yellow_Hue_Value = self.Yellow_Hue_Value.get_value()
        self.Yellow_Saturation_Value = self.Yellow_Saturation_Value.get_value()
        self.Yellow_Value_Value = self.Yellow_Value_Value.get_value()

        self.Object_Hue_Value = self.Object_Hue_Value.get_value()
        self.Object_Saturation_Value = self.Object_Saturation_Value.get_value()
        self.Object_Value_Value = self.Object_Value_Value.get_value()

        self.Finish_Hue_Value = self.Finish_Hue_Value.get_value()
        self.Finish_Saturation_Value = self.Finish_Saturation_Value.get_value()
        self.Finish_Value_Value = self.Finish_Value_Value.get_value()

    def update_sliders(self, blue_hue, blue_sat, blue_value,
                       yellow_hue, yellow_sat, yellow_value,
                       object_hue, object_sat, object_value,
                       finish_hue, finish_sat, finish_value,):
        self.Blue_Hue_Slider.unblit_and_reblit_func(
            self.Blue_Hue_Slider.set_value,
            value=blue_hue)
        self.Blue_Saturation_Slider.unblit_and_reblit_func(
            self.Blue_Saturation_Slider.set_value,
            value=blue_sat)
        self.Blue_Value_Slider.unblit_and_reblit_func(
            self.Blue_Value_Slider.set_value,
            value=blue_value)

        self.Yellow_Hue_Slider.unblit_and_reblit_func(
            self.Yellow_Hue_Slider.set_value,
            value=yellow_hue)
        self.Yellow_Saturation_Slider.unblit_and_reblit_func(
            self.Yellow_Saturation_Slider.set_value,
            value=yellow_sat)
        self.Yellow_Value_Slider.unblit_and_reblit_func(
            self.Yellow_Value_Slider.set_value,
            value=yellow_value)

        self.Object_Hue_Slider.unblit_and_reblit_func(
            self.Object_Hue_Slider.set_value,
            value=object_hue)
        self.Object_Saturation_Slider.unblit_and_reblit_func(
            self.Object_Saturation_Slider.set_value,
            value=object_sat)
        self.Object_Value_Slider.unblit_and_reblit_func(
            self.Object_Value_Slider.set_value,
            value=object_value)

        self.Finish_Hue_Slider.unblit_and_reblit_func(
            self.Finish_Hue_Slider.set_value,
            value=finish_hue)
        self.Finish_Saturation_Slider.unblit_and_reblit_func(
            self.Finish_Saturation_Slider.set_value,
            value=finish_sat)
        self.Finish_Value_Slider.unblit_and_reblit_func(
            self.Finish_Value_Slider.set_value,
            value=finish_value)

    def display_text(self, text, xpos, ypos, font_size):
        self.text = str(text)
        self.text_font_object = pygame.font.SysFont(name=self.text_font,
                                                    size=font_size)
        self.display_text = self.text_font_object.render(text=self.text,
                                                         antialias=True,
                                                         color=self.text_color)
        self.screen.blit(self.display_text, (xpos, ypos))

    def update_frame(self, cv_image):
        cv_image = imutils.resize(cv_image, width=min(self.frame_width,
                                                      cv_image.shape[1]))
        self.frame = cv2.cvtColor(cv_image, cv2.COLOR_BGR2RGB)
        self.frame = np.rot90(self.frame)
        self.frame = pygame.surfarray.make_surface(self.frame)
        self.screen.blit(self.frame, (0, 0))
        self.menu_content.blit()
        self.menu_content.update()
        pygame.display.update()

    def process_events(self):
        pygame.event.pump()
        for event in pygame.event.get():
            self.menu.react(event)

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
