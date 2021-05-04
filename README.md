# geseture-contollered-Tello-using-mediapipe-hands
control the DJI Tello using single hand gestures
open media drone test is the file that runs the whole algorithm
using mediapipe handlandmark recoginition i have created 11 gestures to pilot the DJI Tello quad copter to pilot the drone.
following are the exmaples of gestures:
**forward**
![image](https://user-images.githubusercontent.com/44557919/116989163-4884d180-acc9-11eb-9e10-e34de6d7e3d9.png)
**back**
![image](https://user-images.githubusercontent.com/44557919/116989215-5c303800-acc9-11eb-8942-5482b401f781.png)
**Yaw right**
![image](https://user-images.githubusercontent.com/44557919/116989280-766a1600-acc9-11eb-845c-3ac016e66e5f.png)
**Yaw Left**
![image](https://user-images.githubusercontent.com/44557919/116989326-841f9b80-acc9-11eb-9d3f-d9ed51de0bd0.png)
**Gesture	==> Command**
Thumb touching index finger	==> Forward speed 20cm
Thumb touching middle finger ==>	Backward speed 20cm
Thumb touching ring finger ==>	Yaw right speed 20cm
Thumb touching pinky finger ==>	Yaw left  speed 20cm
Thumb touching index and middle fingers(Worse performing gesture) ==>	Roll right speed 20cm
Thumb touching pinky and ring fingers	 ==> Roll left speed 20cm
Thumb touching middle, ring and index fingers ==>	Go down speed 20cm
Thumb touching middle and ring fingers	==> Go up speed 20cm
Thumb touching middle, ring and pinky ==>	Take off
Thumb touching all fingers	==> land
All fingers open	==> Stop all movements. Speed in all directions = 0

load the helplermod.py in the kernel first before running openMediaDroneTest.py

