# -*- coding: utf-8 -*-
"""
Created on Sun Apr 25 16:57:53 2021

@author: najkh
"""

import cv2
import math
import mediapipe as mp
mp_drawing = mp.solutions.drawing_utils
mp_hands = mp.solutions.hands
import pprint
from djitellopy import Tello
#from easytello import tello
import cv2
import time

#list of gesture mapped to commands
guestures = ["fly","land","forward","backward","yawRight","yawLeft","stop","rollLeft","rollRight","up","down"]

# Drone states
in_flight = False
yawing_left = False
yawing_right = False
moving_forward = False
moving_back = False
moving_up = False
moving_down = False
rolling_left = False
rolling_right = False
stop = True

# method to check if fingers are parallel
def is_parallel(pointA,pointB,pointC):
    # slope = y2-y1/x2-x1
    slopeOne = (pointA.y-pointB.y)/(pointA.x-pointB.x)
    slopeTwo = (pointB.y-pointC.y)/(pointB.x-pointC.x)
    slopeRatio = slopeOne/slopeTwo
    if slopeRatio == 0:
        return True
    
# method to check angle of finger   
def angle_check(pointA,pointB,pointC):
    slopeOne = (pointA.y-pointB.y)/(pointA.x-pointB.x)
    slopeTwo = (pointB.y-pointC.y)/(pointB.x-pointC.x)
    lineAngle = math.atan((slopeOne-slopeTwo)/(1+slopeOne*slopeTwo))
    return lineAngle
# this function calculate 2D(x,y) distance of points provided in parameters
def find_distance(pointA,pointB):
    return math.sqrt((pointB.x-pointA.x)**2+(pointB.y-pointA.y)**2)

def one_dimensional_distance(pointA,pointB):
    return math.sqrt((pointB-pointA)**2)

# function that detects gestures from hand landmarks provided by MediaPipe
def find_gestures(handLandmarks):
    
    # index finger dip and tip coordinates
    index_dip = handLandmarks.landmark[mp_hands.HandLandmark.INDEX_FINGER_DIP]
    index_tip = handLandmarks.landmark[mp_hands.HandLandmark.INDEX_FINGER_TIP]
    
    # Three point on middle finger
    middle_mcp = handLandmarks.landmark[mp_hands.HandLandmark.MIDDLE_FINGER_MCP]
    middle_dip = handLandmarks.landmark[mp_hands.HandLandmark.MIDDLE_FINGER_DIP]
    middle_tip = handLandmarks.landmark[mp_hands.HandLandmark.MIDDLE_FINGER_TIP]
    
    # Thumb tip coordinates
    thumb_tip = handLandmarks.landmark[mp_hands.HandLandmark.THUMB_TIP]
    
    # Ring finger tip and dip coordinates
    ring_tip = handLandmarks.landmark[mp_hands.HandLandmark.RING_FINGER_TIP]
    ring_dip = handLandmarks.landmark[mp_hands.HandLandmark.RING_FINGER_DIP]
    
    # Pinky finger tip and dip coordinates
    pinky_tip = handLandmarks.landmark[mp_hands.HandLandmark.PINKY_TIP]
    pinky_dip = handLandmarks.landmark[mp_hands.HandLandmark.PINKY_DIP]
   
    # Thumb and middle finger tip distance
    th_mid_dis = find_distance(middle_tip,thumb_tip)
    # Thumb and index finger tip distance
    th_in_dis = find_distance(index_tip, thumb_tip)
    # Thumb and ring finger tip distance
    th_ring_dis = find_distance(ring_tip,thumb_tip)
    # Thumb and pinky finger tip distance
    th_pinky_dis = find_distance(pinky_tip,thumb_tip)
    
    # Thumb touching Middle finger Tip
    if th_mid_dis < 0.05 and th_in_dis > 0.05 and th_ring_dis > 0.05 and th_pinky_dis > 0.05:
        return 3
    
    # Thumb touching index finger Tip
    if th_in_dis < 0.05 and th_mid_dis > 0.05 and th_ring_dis > 0.05 and th_pinky_dis > 0.05:
        return 2
        
   # Thumb touching ring finger Tip
    if th_ring_dis < 0.05 and th_in_dis > 0.05 and th_mid_dis > 0.05 and th_pinky_dis > 0.05:
        return 4
        
    # Thumb touching pinky finger Tip
    if th_pinky_dis < 0.05 and th_in_dis > 0.05 and th_mid_dis > 0.05 and th_ring_dis > 0.05:
        return 5
        
    # Thumb touching ring and pink fingers Tip
    if th_pinky_dis < 0.05 and th_ring_dis < 0.05 and th_in_dis > 0.05 and th_mid_dis > 0.05 :
        return 7
        
    # Thumb touching index and middle fingers Tip
    if th_in_dis < 0.08 and th_mid_dis < 0.08 and th_ring_dis > 0.05 and th_pinky_dis > 0.05:
        return 8
        
    # Thumb touching ring and middle fingers Tip
    if th_mid_dis < 0.05 and th_ring_dis < 0.05 and th_in_dis > 0.05 and th_pinky_dis > 0.05:
        return 9
       
    # Thumb touching middle, ring and pinky fingers Tip
    if th_ring_dis < 0.05 and th_pinky_dis < 0.05 and th_mid_dis < 0.05 and th_in_dis > 0.05:
        return 0
    
    # Thumb touching middle, ring and index fingers Tip
    if th_ring_dis < 0.1 and th_mid_dis < 0.1 and th_in_dis < 0.1 and th_pinky_dis > 0.08 :
        return 10
       
    # Thumb touching all finger Tips
    if th_ring_dis < 0.08 and th_mid_dis < 0.08 and th_in_dis < 0.08 and th_pinky_dis < 0.08 :
        return 1
    
    # check if all fingers are open
    if index_tip.y < index_dip.y and middle_tip.y < middle_dip.y and ring_tip.y < ring_dip.y and pinky_tip.y < pinky_dip.y:
        return 6
    
    # if no detection return -1
    return -1

# function to normalise gestures takes 5 consecutive gesture to send one command
def guesture_normalisation(guesture,consec_guestures):
    # if there is a gesture detected
    if(guesture != -1):
        # if no gestures in the consec_guestures then add new gesture to it
        if len(consec_guestures) == 0:
            consec_guestures.append(guesture)
        else:
            if(consec_guestures[-1] == guesture):
                consec_guestures.append(guesture)
            else:
                consec_guestures.clear()
                consec_guestures.append(guesture)
            if len(consec_guestures) == 5:
                    temp = guestures[consec_guestures[-1]]
                    print("command = " + temp)
                    consec_guestures.clear()
                    return temp
                
# this function maps gestures to appropriate commands and then sends them to Tello
def parse_command(command,drone):
    global in_flight, moving_back, moving_forward, yawing_left, yawing_right
    global rolling_left, rolling_right, moving_up, moving_down
    # send land command
    if command == "land":
        in_flight == False
        drone.land()
        print("landing sucessfull")
        
    # send takeoff command to Tello
    if command == "fly" and not in_flight:
        in_flight = True
        drone.takeoff()
    
    # send move forward command to Tello
    if command == "forward" and not moving_forward:
        # following is legend for send_rc_control command
        #send_rc_control(self, left_right_velocity, forward_backward_velocity, up_down_velocity, yaw_velocity)
        drone.send_rc_control(0, 20, 0, 0)
        yawing_left = False
        yawing_right = False
        moving_forward = True
        moving_back = False
        moving_up = False
        moving_down = False
        rolling_left = False
        rolling_right = False

    # send move back command to Tello    
    if command == "backward" and not moving_back:
        #drone.move_back(20)
        drone.send_rc_control(0, -20, 0, 0)
        yawing_left = False
        yawing_right = False
        moving_forward = False
        moving_back = True
        moving_up = False
        moving_down = False
        rolling_left = False
        rolling_right = False

    # send yaw left command to Tello
    if command == "yawLeft" and not yawing_left:
        drone.send_rc_control(0, 0, 0, 20)
        yawing_left = True
        yawing_right = False
        moving_forward = False
        moving_back = False
        moving_up = False
        moving_down = False
        rolling_left = False
        rolling_right = False
    
    # send yaw right command to Tello
    if command == "yawRight" and not yawing_right:
        drone.send_rc_control(0, 0, 0, -20)
        yawing_left = False
        yawing_right = True
        moving_forward = False
        moving_back = False
        moving_up = False
        moving_down = False
        rolling_left = False
        rolling_right = False
        
    # send roll left command to Tello    
    if command == "rollLeft" and not rolling_left:
        drone.send_rc_control(-20, 0, 0, 0)
        yawing_left = False
        yawing_right = False
        moving_forward = False
        moving_back = False
        moving_up = False
        moving_down = False
        rolling_left = True
        rolling_right = False
        
    # send roll right command to Tello        
    if command == "rollRight" and not rolling_right:
        drone.send_rc_control(20, 0, 0, 0)
        yawing_left = False
        yawing_right = False
        moving_forward = False
        moving_back = False
        moving_up = False
        moving_down = False
        rolling_left = False
        rolling_right = True
      
    # send move up command to Tello    
    if command == "up" and not moving_up:
        drone.send_rc_control(0, 0, 20, 0)
        yawing_left = False
        yawing_right = False
        moving_forward = False
        moving_back = False
        moving_up = True
        moving_down = False
        rolling_left = False
        rolling_right = False
        
    # send move down command to Tello
    if command == "down" and not moving_down:
        drone.send_rc_control(0, 0, -20, 0)
        yawing_left = False
        yawing_right = False
        moving_forward = False
        moving_back = False
        moving_up = False
        moving_down = True
        rolling_left = False
        rolling_right = False
        
    # send stop command to Tello
    if command == "stop":
        drone.send_rc_control(0, 0, 0, 0)
        yawing_left = False
        yawing_right = False
        moving_forward = False
        moving_back = False
        moving_up = False
        moving_down = False
        rolling_left = False
        rolling_right = False
        
