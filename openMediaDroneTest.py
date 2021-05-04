# -*- coding: utf-8 -*-
"""
Created on Sun Apr 18 19:36:33 2021

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


######################################################################
width = 420  # WIDTH OF THE IMAGE
height = 340  # HEIGHT OF THE IMAGE
startCounter =0   #  0 FOR FIGHT 1 FOR TESTING
######################################################################


# CONNECT TO TELLO
me = Tello()
me.connect()
me.for_back_velocity = 0
me.left_right_velocity = 0
me.up_down_velocity = 0
me.yaw_velocity = 0
me.speed = 0

me.streamoff()
me.streamon()

# print drone's battery level
print(me.get_battery())

font = cv2.FONT_HERSHEY_SIMPLEX

# array to temperarily store gestures
consec_guestures = []

# For webcam input:
cap = cv2.VideoCapture(0)
with mp_hands.Hands(
    min_detection_confidence=0.70,
    min_tracking_confidence=0.70) as hands:
  while cap.isOpened():
    
    # GET THE IMGAE FROM TELLO
    tello_frame = me.get_frame_read()
    myFrame = tello_frame.frame
    img = cv2.resize(myFrame, (width, height))
    start_time = time.time()
    # read video from laptop's camera
    success, image = cap.read()
    
    # if there is no video feed print error message
    if not success:
      print("Ignoring empty camera frame.")
      # If loading a video, use 'break' instead of 'continue'.
      continue

    # the BGR image to RGB.
    image = cv2.cvtColor(cv2.flip(image, 1), cv2.COLOR_BGR2RGB)
    # To improve performance, optionally mark the image as not writeable to
    # pass by reference.
    image.flags.writeable = False
    results = hands.process(image)

    # Draw the hand annotations on the image.
    image.flags.writeable = True
    image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)
    
    # if hand landmarks are detect then pass those to gestesture detection algorithm
    if results.multi_hand_landmarks:
      
      for hand_landmarks in results.multi_hand_landmarks:
          # find gestures, normalise them and send to parse_command method which maps 
          # gestures to commands all these methods are from helperMod.py
          parse_command(guesture_normalisation(find_gestures(hand_landmarks),consec_guestures),me)
          # draw handland marks on the video feed recieved from laptop's camera    
          mp_drawing.draw_landmarks(image, hand_landmarks, mp_hands.HAND_CONNECTIONS)
    current_time = time.time()
    # calculate frame rate of detections
    fps = ""
    if current_time-start_time != 0:
        fps = str(int(1/(current_time-start_time)))
    start_time = current_time
    # write frame rate to image
    cv2.putText(image,fps,(10,50), font, 1,(255,255,255),2)
    # display footage from drone      
    cv2.imshow('Drone', img)
    # display footage from laptop's camera
    cv2.imshow('MediaPipe Hands', image)
    # break loop on escape key press
    if cv2.waitKey(5) & 0xFF == 27:
      break
# release the cap, stop stream from Tello and distroy all created windows
cap.release()
me.streamoff()
cv2.destroyAllWindows()





            
            
            