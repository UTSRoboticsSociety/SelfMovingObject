import pygame

pygame.init()





pygame.joystick.init()

# -------- Main Program Loop -----------
while done==False:
    # EVENT PROCESSING STEP
    for event in pygame.event.get(): # User did something
        if event.type == pygame.QUIT: # If user clicked close
            done=True # Flag that we are done so we exit this loop

        # Possible joystick actions: JOYAXISMOTION JOYBALLMOTION JOYBUTTONDOWN JOYBUTTONUP JOYHATMOTION
        if event.type == pygame.JOYBUTTONDOWN:
            print("Joystick button pressed.")
        if event.type == pygame.JOYBUTTONUP:
            print("Joystick button released.")

    #joystick_count = pygame.joystick.get_count()

    for i in range(joystick_count):
        joystick = pygame.joystick.Joystick(0)
        joystick.init()
        axis0 = joystick.get_axis(0)  #Left / Right on left joystick
        axis1 = joystick.get_axis(1)  #Up / Dpwn on left joystick
        axis2 = joystick.get_axis(2)  #R2 / L2 L2 is positive, R2 is negative.
        button = joystick.get_button(0) #A Button
