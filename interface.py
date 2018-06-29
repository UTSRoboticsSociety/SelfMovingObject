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

        self.Upper_Hue_Slider = None
        self.Upper_Saturation_Slider = None
        self.Upper_Value_Slider = None

        self.Lower_Hue_Slider = None
        self.Lower_Saturation_Slider = None
        self.Lower_Value_Slider = None

        self.Upper_Hue_Inserter = None
        self.Upper_Saturation_Inserter = None
        self.Upper_Value_Inserter = None

        self.Lower_Hue_Inserter = None
        self.Lower_Saturation_Inserter = None
        self.Lower_Value_Inserter = None

        self.Upper_Canny_Inserter = None
        self.Lower_Canny_Inserter = None

        self.lane1_button = None
        self.lane2_button = None
        self.object_button = None
        self.finish_button = None
        self.stop_button = None
        self.quit_button = None
        self.disable_obstacle_button = None

        self.lane1_enable = True
        self.lane2_enable = False
        self.object_enable = False
        self.finish_enable = False

        self.all_stop = False
        self.obstacle_disable = False
        self.color_update_ready = False
        self.exit_run = False

        self.HSV_Lane1_Upper = None
        self.HSV_Lane2_Upper = None
        self.HSV_Object_Upper = None
        self.HSV_Lane1_Lower = None
        self.HSV_Lane2_Lower = None
        self.HSV_Object_Lower = None
        self.HSV_Finish_Upper = None
        self.HSV_Finish_Lower = None

        self.Upper_Canny_Value = None
        self.Lower_Canny_Value = None

        self.slide_limit = 255

        self.menu = None
        self.menu_content = None
        self.menu_slide_reaction = None
        self.menu_inserter_reaction = None

        self.pressed = None

        self.text = None
        self.text_font_object = None
        self.text_font = 'arial'
        self.display_text = None
        self.text_color = (255, 255, 255)

        self.screen = None
        self.frame = None
        self.screen_width = 1600
        self.screen_height = 720
        self.menu_size = 280
        self.frame_width = self.screen_width - self.menu_size
        self.screen_caption = "wasd car control"

        pygame.init()
        pygame.joystick.init()

        self.joystick_count = pygame.joystick.get_count()

    def lane1_update(self):
        self.lane1_enable = True
        self.lane2_enable = False
        self.object_enable = False
        self.finish_enable = False
        self.update_sliders(self.HSV_Lane1_Upper, self.HSV_Lane1_Lower)
        self.update_inserter(self.HSV_Lane1_Upper, self.HSV_Lane1_Lower)

    def lane2_update(self):
        self.lane1_enable = False
        self.lane2_enable = True
        self.object_enable = False
        self.finish_enable = False
        self.update_sliders(self.HSV_Lane2_Upper, self.HSV_Lane2_Lower)
        self.update_inserter(self.HSV_Lane2_Upper, self.HSV_Lane2_Lower)

    def object_update(self):
        self.lane1_enable = False
        self.lane2_enable = False
        self.object_enable = True
        self.finish_enable = False
        self.update_sliders(self.HSV_Object_Upper, self.HSV_Object_Lower)
        self.update_inserter(self.HSV_Object_Upper, self.HSV_Object_Lower)

    def finish_update(self):
        self.lane1_enable = False
        self.lane2_enable = False
        self.object_enable = False
        self.finish_enable = True
        self.update_sliders(self.HSV_Finish_Upper, self.HSV_Finish_Lower)
        self.update_inserter(self.HSV_Finish_Upper, self.HSV_Finish_Lower)

    def stop_update(self):
        if self.all_stop:
            self.all_stop = False
        else:
            self.all_stop = True

    def obstacle_update(self):
        if self.obstacle_disable:
            self.obstacle_disable = False
        else:
            self.obstacle_disable = True

    def create_menu(self):
        self.lane1_button = thorpy.make_button("Lane 1 Color Choice",
                                               func=self.lane1_update)

        self.lane2_button = thorpy.make_button("Lane 2 Color Choice",
                                               func=self.lane2_update)

        self.object_button = thorpy.make_button("Object Color Choice",
                                                func=self.object_update)

        self.finish_button = thorpy.make_button("Finish Line Color Choice",
                                                func=self.finish_update)

        self.disable_obstacle_button = thorpy.make_button(
                                               ("Disable Obstacle Detection"),
                                                func=self.obstacle_update)

        self.stop_button = thorpy.make_button("STOP!!",
                                              func=self.stop_update)

        self.quit_button = thorpy.make_button("Quit",
                                              func=thorpy.functions.quit_func)

        self.Upper_Hue_Inserter = thorpy.Inserter.make(name="Upper Hue:",
                                                       value="0")
        self.Upper_Saturation_Inserter = thorpy.Inserter.make(
                                                             name="Upper Sat:",
                                                             value="0")
        self.Upper_Value_Inserter = thorpy.Inserter.make(name="Upper Value: ",
                                                         value="0")

        self.Lower_Hue_Inserter = thorpy.Inserter.make(name="Lower Hue: ",
                                                       value="0")
        self.Lower_Saturation_Inserter = thorpy.Inserter.make(
                                                             name="Lower Sat:",
                                                             value="0")
        self.Lower_Value_Inserter = thorpy.Inserter.make(name="Lower Value: ",
                                                         value="0")

        self.Upper_Canny_Inserter = thorpy.Inserter.make(
                                                         name="Upper Canny:",
                                                         value="0")
        self.Lower_Canny_Inserter = thorpy.Inserter.make(name="Lower Canny: ",
                                                         value="0")

        self.Upper_Hue_Slider = thorpy.SliderX.make(length=100,
                                                    limvals=(
                                                       0,
                                                       self.slide_limit),
                                                    text="Upper Hue:",
                                                    type_=int)
        self.Upper_Saturation_Slider = thorpy.SliderX.make(length=100,
                                                           limvals=(
                                                             0,
                                                             self.slide_limit),
                                                           text="Upper Sat:",
                                                           type_=int)
        self.Upper_Value_Slider = thorpy.SliderX.make(length=100,
                                                      limvals=(
                                                         0,
                                                         self.slide_limit),
                                                      text="Upper Value:",
                                                      type_=int)

        self.Lower_Hue_Slider = thorpy.SliderX.make(length=100,
                                                    limvals=(
                                                         0,
                                                         self.slide_limit),
                                                    text="Lower Hue:",
                                                    type_=int)
        self.Lower_Saturation_Slider = thorpy.SliderX.make(length=100,
                                                           limvals=(
                                                             0,
                                                             self.slide_limit),
                                                           text="Lower Sat:",
                                                           type_=int)
        self.Lower_Value_Slider = thorpy.SliderX.make(length=100,
                                                      limvals=(
                                                           0,
                                                           self.slide_limit),
                                                      text="Lower Value:",
                                                      type_=int)

        self.menu_content = thorpy.Box.make(elements=[
            self.lane1_button,
            self.lane2_button,
            self.object_button,
            self.finish_button,
            self.disable_obstacle_button,
            self.stop_button,
            self.Upper_Hue_Slider,
            self.Upper_Saturation_Slider,
            self.Upper_Value_Slider,
            self.Lower_Hue_Slider,
            self.Lower_Saturation_Slider,
            self.Lower_Value_Slider,
            self.Upper_Hue_Inserter,
            self.Upper_Saturation_Inserter,
            self.Upper_Value_Inserter,
            self.Lower_Hue_Inserter,
            self.Lower_Saturation_Inserter,
            self.Lower_Value_Inserter,
            self.Upper_Canny_Inserter,
            self.Lower_Canny_Inserter,
            self.quit_button])

        self.menu_slide_reaction = thorpy.Reaction(
            reacts_to=thorpy.constants.THORPY_EVENT,
            reac_func=self.react_slider,
            event_args={"id": thorpy.constants.EVENT_SLIDE},
            reac_name="slider reaction")
        self.menu_content.add_reaction(self.menu_slide_reaction)

        self.menu_inserter_reaction = thorpy.Reaction(
            reacts_to=thorpy.constants.THORPY_EVENT,
            reac_func=self.react_inserter,
            event_args={"id": thorpy.constants.EVENT_INSERT},
            reac_name="inserter reaction")

        self.menu_content.add_reaction(self.menu_inserter_reaction)

        self.menu = thorpy.Menu(self.menu_content)

        for element in self.menu.get_population():
            element.surface = self.screen

        self.lane1_update()
        self.menu_content.set_topleft((self.frame_width, 100))
        self.menu_content.blit()
        self.menu_content.update()

    def get_slider_values(self):
        self.color_update_ready = False
        return (
            self.HSV_Lane1_Upper,
            self.HSV_Lane2_Upper,
            self.HSV_Object_Upper,
            self.HSV_Lane1_Lower,
            self.HSV_Lane2_Lower,
            self.HSV_Object_Lower,
            self.HSV_Finish_Upper,
            self.HSV_Finish_Lower,
            self.Upper_Canny_Value,
            self.Lower_Canny_Value
        )

    def get_all_stop(self):
        return self.all_stop

    def get_obstacle_detect(self):
        return self.obstacle_disable

    def color_update_ready_call(self):
        return self.color_update_ready

    def react_inserter(self, event):
        self.color_update_ready = True
        self.Upper_Canny_Value = int(self.Upper_Canny_Inserter.get_value())
        self.Lower_Canny_Value = int(self.Lower_Canny_Inserter.get_value())
        if self.lane1_enable:
            self.HSV_Lane1_Upper = np.array(
                [int(self.Upper_Hue_Inserter.get_value()),
                 int(self.Upper_Saturation_Inserter.get_value()),
                 int(self.Upper_Value_Inserter.get_value())])

            self.HSV_Lane1_Lower = np.array(
                [int(self.Lower_Hue_Inserter.get_value()),
                 int(self.Lower_Saturation_Inserter.get_value()),
                 int(self.Lower_Value_Inserter.get_value())])
            self.update_sliders(self.HSV_Lane1_Upper, self.HSV_Lane1_Lower)

        elif self.lane2_enable:
            self.HSV_Lane2_Upper = np.array(
                [int(self.Upper_Hue_Inserter.get_value()),
                 int(self.Upper_Saturation_Inserter.get_value()),
                 int(self.Upper_Value_Inserter.get_value())])

            self.HSV_Lane2_Lower = np.array(
                [int(self.Lower_Hue_Inserter.get_value()),
                 int(self.Lower_Saturation_Inserter.get_value()),
                 int(self.Lower_Value_Inserter.get_value())])
            self.update_sliders(self.HSV_Lane2_Upper, self.HSV_Lane2_Lower)

        elif self.object_enable:
            self.HSV_Object_Upper = np.array(
                [int(self.Upper_Hue_Inserter.get_value()),
                 int(self.Upper_Saturation_Inserter.get_value()),
                 int(self.Upper_Value_Inserter.get_value())])

            self.HSV_Object_Lower = np.array(
                [int(self.Lower_Hue_Inserter.get_value()),
                 int(self.Lower_Saturation_Inserter.get_value()),
                 int(self.Lower_Value_Inserter.get_value())])
            self.update_sliders(self.HSV_Object_Upper, self.HSV_Object_Lower)

        elif self.finish_enable:
            self.HSV_Finish_Upper = np.array(
                [int(self.Upper_Hue_Inserter.get_value()),
                 int(self.Upper_Saturation_Inserter.get_value()),
                 int(self.Upper_Value_Inserter.get_value())])

            self.HSV_Finish_Lower = np.array(
                [int(self.Lower_Hue_Inserter.get_value()),
                 int(self.Lower_Saturation_Inserter.get_value()),
                 int(self.Lower_Value_Inserter.get_value())])
            self.update_sliders(self.HSV_Finish_Upper, self.HSV_Finish_Lower)



    def react_slider(self, event):
        self.color_update_ready = True

        if self.lane1_enable:
            self.HSV_Lane1_Upper = np.array(
                [self.Upper_Hue_Slider.get_value(),
                 self.Upper_Saturation_Slider.get_value(),
                 self.Upper_Value_Slider.get_value()])

            self.HSV_Lane1_Lower = np.array(
                [self.Lower_Hue_Slider.get_value(),
                 self.Lower_Saturation_Slider.get_value(),
                 self.Lower_Value_Slider.get_value()])
            self.update_inserter(self.HSV_Lane1_Upper, self.HSV_Lane1_Lower)

        elif self.lane2_enable:
            self.HSV_Lane2_Upper = np.array(
                [self.Upper_Hue_Slider.get_value(),
                 self.Upper_Saturation_Slider.get_value(),
                 self.Upper_Value_Slider.get_value()])

            self.HSV_Lane2_Lower = np.array(
                [self.Lower_Hue_Slider.get_value(),
                 self.Lower_Saturation_Slider.get_value(),
                 self.Lower_Value_Slider.get_value()])
            self.update_inserter(self.HSV_Lane2_Upper, self.HSV_Lane2_Lower)

        elif self.object_enable:
            self.HSV_Object_Upper = np.array(
                [self.Upper_Hue_Slider.get_value(),
                 self.Upper_Saturation_Slider.get_value(),
                 self.Upper_Value_Slider.get_value()])

            self.HSV_Object_Lower = np.array(
                [self.Lower_Hue_Slider.get_value(),
                 self.Lower_Saturation_Slider.get_value(),
                 self.Lower_Value_Slider.get_value()])
            self.update_inserter(self.HSV_Object_Upper, self.HSV_Object_Lower)

        elif self.finish_enable:
            self.HSV_Finish_Upper = np.array(
                [self.Upper_Hue_Slider.get_value(),
                 self.Upper_Saturation_Slider.get_value(),
                 self.Upper_Value_Slider.get_value()])

            self.HSV_Finish_Lower = np.array(
                [self.Lower_Hue_Slider.get_value(),
                 self.Lower_Saturation_Slider.get_value(),
                 self.Lower_Value_Slider.get_value()])
            self.update_inserter(self.HSV_Finish_Upper, self.HSV_Finish_Lower)

    def update_sliders(self, upper_hsv_values, lower_hsv_values):

        self.Upper_Hue_Slider.unblit_and_reblit_func(
            self.Upper_Hue_Slider.set_value,
            value=upper_hsv_values[0])
        self.Upper_Saturation_Slider.unblit_and_reblit_func(
            self.Upper_Saturation_Slider.set_value,
            value=upper_hsv_values[1])
        self.Upper_Value_Slider.unblit_and_reblit_func(
            self.Upper_Value_Slider.set_value,
            value=upper_hsv_values[2])

        self.Lower_Hue_Slider.unblit_and_reblit_func(
            self.Lower_Hue_Slider.set_value,
            value=lower_hsv_values[0])
        self.Lower_Saturation_Slider.unblit_and_reblit_func(
            self.Lower_Saturation_Slider.set_value,
            value=lower_hsv_values[1])
        self.Lower_Value_Slider.unblit_and_reblit_func(
            self.Lower_Value_Slider.set_value,
            value=lower_hsv_values[2])

    def update_inserter(self, upper_hsv_values, lower_hsv_values):

        self.Upper_Hue_Inserter.unblit_and_reblit_func(
            self.Upper_Hue_Inserter.set_value,
            value=str(upper_hsv_values[0]))
        self.Upper_Saturation_Inserter.unblit_and_reblit_func(
            self.Upper_Saturation_Inserter.set_value,
            value=str(upper_hsv_values[1]))
        self.Upper_Value_Inserter.unblit_and_reblit_func(
            self.Upper_Value_Inserter.set_value,
            value=str(upper_hsv_values[2]))

        self.Lower_Hue_Inserter.unblit_and_reblit_func(
            self.Lower_Hue_Inserter.set_value,
            value=str(lower_hsv_values[0]))
        self.Lower_Saturation_Inserter.unblit_and_reblit_func(
            self.Lower_Saturation_Inserter.set_value,
            value=str(lower_hsv_values[1]))
        self.Lower_Value_Inserter.unblit_and_reblit_func(
            self.Lower_Value_Inserter.set_value,
            value=str(lower_hsv_values[2]))

        self.Upper_Canny_Inserter.unblit_and_reblit_func(
            self.Upper_Canny_Inserter.set_value,
            value=str(self.Upper_Canny_Value))

        self.Lower_Canny_Inserter.unblit_and_reblit_func(
            self.Lower_Canny_Inserter.set_value,
            value=str(self.Lower_Canny_Value))

    def define_hsv_colours(self,
                           HSV_Blue_Upper,
                           HSV_Yellow_Upper,
                           HSV_Object_Upper,
                           HSV_Blue_Lower,
                           HSV_Yellow_Lower,
                           HSV_Object_Lower,
                           HSV_Finish_Upper,
                           HSV_Finish_Lower,
                           canny_low,
                           canny_high):

        self.HSV_Lane1_Upper = HSV_Blue_Upper
        self.HSV_Lane2_Upper = HSV_Yellow_Upper
        self.HSV_Object_Upper = HSV_Object_Upper
        self.HSV_Lane1_Lower = HSV_Blue_Lower
        self.HSV_Lane2_Lower = HSV_Yellow_Lower
        self.HSV_Object_Lower = HSV_Object_Lower
        self.HSV_Finish_Upper = HSV_Finish_Upper
        self.HSV_Finish_Lower = HSV_Finish_Lower
        self.Lower_Canny_Value = canny_low
        self.Upper_Canny_Value = canny_high

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
        self.frame = cv2.flip(self.frame, 1)
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
            if event.type == pygame.QUIT:
                self.exit_run = True

    def exit_check(self):
        return self.exit_run

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
            self.backward = False

        elif (self.pressed[pygame.K_s]):
            self.backward = True
            self.forward = False
        else:
            self.forward = False
            self.backward = False

        if (self.pressed[pygame.K_a]):
            self.left = True
            self.right = False
        elif (self.pressed[pygame.K_d]):
            self.right = True
            self.left = False
        else:
            self.left = False
            self.right = False

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
