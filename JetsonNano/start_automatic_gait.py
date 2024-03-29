"""
Simulation of SpotMicroAI and it's Kinematics 
Use a keyboard to see how it works
Use keyboard-Button to switch betweek walk on static-mode
"""
from os import system, name 
import sys
sys.path.append("..")

import matplotlib.animation as animation
import numpy as np
import time
import math
import datetime as dt
import keyboard
import random

import Kinematics.kinematics as kn
import spotmicroai
import servo_controller

from multiprocessing import Process
from multiprocess_kb import KeyInterrupt
from Kinematics.kinematicMotion import KinematicMotion, TrottingGait
import logging
# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


rtime=time.time()

def reset():
    global rtime
    rtime=time.time()    

robot=spotmicroai.Robot(False,False,reset)
controller = servo_controller.Controllers()

# TODO: Needs refactoring
speed1=240
speed2=170
speed3=300

speed1=322
speed2=237
speed3=436

spurWidth=robot.W/2+20
stepLength=0
stepHeight=72

# Initial End point X Value for Front legs 
iXf=120

walk=False

def resetPose():
    # TODO: globals are bad
    global joy_x, joy_z, joy_y, joy_rz, joy_z
    joy_x, joy_y, joy_z, joy_rz = 128, 128, 128, 128

# define our clear function 
def consoleClear(): 
  
    # for windows 
    if name == 'nt': 
        _ = system('cls') 
  
    # for mac and linux(here, os.name is 'posix') 
    else: 
        _ = system('clear') 



Lp = np.array([[iXf, -130, spurWidth, 1], [iXf, -130, -spurWidth, 1],
[-50, -130, spurWidth, 1], [-50, -130, -spurWidth, 1]])

motion=KinematicMotion(Lp)
resetPose()

trotting=TrottingGait()

def main(id, command_status):
    jointAngles = []
    while True:
        xr = 0.0
        yr = 0.0

        # Reset when robot pose become strange
        # robot.resetBody()
    
        ir=xr/(math.pi/180)
        
        d=time.time()-rtime

        # robot height
        height = 40

        # calculate robot step command from keyboard inputs
        result_dict = command_status.get()
        logging.info(result_dict)
        command_status.put(result_dict)

        # wait 3 seconds to start
        if result_dict.get('StartStepping',False):
            currentLp = trotting.positions(d-3, result_dict)
            robot.feetPosition(currentLp)
        else:
            robot.feetPosition(Lp)
            result_dict['StartStepping'] = True
        #roll=-xr
        roll=0
        robot.bodyRotation((roll,math.pi/180*((joy_x)-128)/3,-(1/256*joy_y-0.5)))
        bodyX=50+yr*10
        robot.bodyPosition((bodyX, 40+height, -ir))

        # Get current Angles for each motor
        jointAngles = robot.getAngle()
        logging.info("Joint angles: %s", jointAngles)
        
        if len(jointAngles) == 0:
            logging.info("No joint angles")
        
        else:
            # Rotate the servo motors   
            controller.servoRotate(jointAngles)
            # # Plot Robot Pose into Matplotlib for Debugging
            # kn.initFK(jointAngles)
            # kn.plotKinematics()

        robot.step()
        consoleClear()


if __name__ == "__main__":
    # try:
    # Keyboard input Process
    KeyInputs = KeyInterrupt()
    KeyProcess = Process(target=KeyInputs.keyInterrupt, args=(1, KeyInputs.key_status, KeyInputs.command_status))
    KeyProcess.start()

    # Main Process 
    main(2, KeyInputs.command_status)
    
    logging.info("Terminate KeyBoard Input process")
    if KeyProcess.is_alive():
        KeyProcess.terminate()
    # except Exception as e:
    #     logging.info(e)
    # finally:
    #     logging.info("Done... :)")