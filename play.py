#!/usr/bin/env python
import os

os.environ["CUDA_VISIBLE_DEVICES"]="-1"    
from utils import resize_image, XboxController,Screenshot
from termcolor import cprint
from train import create_model
import numpy as np
from playf1 import playitboy
import mss
from PIL import ImageTk, Image
import vgamepad as vg
import time
gamepad = vg.VX360Gamepad()

def take_screenshot():
    # Get raw pixels from the screen
    sct = mss.mss()
    sct_img = sct.grab({  "top": Screenshot.OFFSET_Y,
                              "left": Screenshot.OFFSET_X,
                             "width": Screenshot.SRC_W,
                            "height": Screenshot.SRC_H})

    # Create the Image
    return Image.frombytes('RGB', sct_img.size, sct_img.bgra, 'raw', 'BGRX')

# Play
class Actor(object):

    def __init__(self):
        # Load in model from train.py and load in the trained weights
        self.model = create_model(keep_prob=1) # no dropout
        self.model.load_weights('model_weights.h5')

        # Init contoller for manual override
        self.real_controller = XboxController()

    def get_action(self, obs):

        ### determine manual override
        manual_override = self.real_controller.LeftBumper == 1

        if not manual_override:
            ## Look
            #vec = resize_image(obs)
            #vec = obs.reshape((Sample.IMG_H, Sample.IMG_W, Sample.IMG_D))
            vec = np.expand_dims(obs, axis=0) # expand dimensions for predict, it wants (1,66,200,3) not (66, 200, 3)
            ## Think
            joystick = self.model.predict(vec, batch_size=1)[0]

        else:
            joystick = self.real_controller.read()
            joystick[1] *= -1 # flip y (this is in the config when it runs normally)


        ## Act

        ### calibration
        output = [
            (joystick[0]),
            (joystick[1]),
            ((joystick[2])),
            ((joystick[3])),
            int(round(joystick[4])),
        ]

        ### print to console
        if manual_override:
            cprint("Manual: " + str(output), 'yellow')
        else:
            cprint("AI: " + str(output), 'green')

        return output


if __name__ == '__main__':
    '''env = gym.make('Mario-Kart-Royal-Raceway-v0')
            
                obs = env.reset()
                env.render()
                print('env ready!')'''
    gamepad.press_button(button=vg.XUSB_BUTTON.XUSB_GAMEPAD_A)
    gamepad.update()
    time.sleep(2)
    gamepad.release_button(button=vg.XUSB_BUTTON.XUSB_GAMEPAD_A)
    gamepad.update()
    time.sleep(2)
    obs = take_screenshot()


    actor = Actor()
    print('actor ready!')

    print('beginning episode loop')
    '''total_reward = 0
                end_episode = False'''
    j =0
    while True :
        action = actor.get_action(obs)
        playitboy(action)
        obs = take_screenshot()
        #obs.save(f"{j}.png")
        j=j+1
        #   obs, reward, end_episode, info = env.step(action)
        #   env.render()
        #   total_reward += reward

    '''print('end episode... total reward: ' + str(total_reward))
            
                obs = env.reset()
                print('env ready!')
            
                input('press <ENTER> to quit')
            
                env.close()'''
