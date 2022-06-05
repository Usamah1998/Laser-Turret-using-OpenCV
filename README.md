# Laser-Turret-using-OpenCV
A laser pointer turret that aims at and follows target objects within its view.The turret consists of a laser attached to two servo motors controlling horizontal and vertical aim. Uses a arduino to control the laser and a hand detection algorithm using OpenCV and cvzone. The center of the bounding box of the largest contour detected by OpenCV is used as the target for the laser to track.The algorithm can be configured to detect different objects using cvzone like face, shapes, colors and many other objects using cvzone library with OpenCV. It also calculate the distance of the object using which accurate angles is calculated for the X-Y servos.
## Implementation
### Calculating Focal Length
First the focal length of the camera must be calculated using a set of images. First we execute the script `Capture_ref_image.py` and a window pops up with camera feed. Then, we put our hand(or the target object) at a distance of exact `84cm` from the camera and take a series of pictures by pressing `c`. Which will be stored in a file `capture_images`. This known distance(84cm) can be changed in `Utils.py` by chanhing the value of variable `Known_distance`. The average known width of the hand from bottom of Index finger to Pinky finger is `6.3cm`. This Known width(6.3cm) can be changed in `Utils.py` by chanhing the value of variable `Known_width`. Using the formula:

              focal_length = (virtual_width * known_distance)/known_width
              
Where virtual width is calculated by OpenCV and known_distance, known_width is explained above. we find the focal length of the camera.To get more accurate focal length we find focal length for all images and take average of them. (This formulae is derived by using Ray optics and trignometry)
### Calculating Distance
Once the focal length is calculated we find distance of each detected object using the formulae:

              distance = (Known_width * focal_length)/virtual_width
 
 Where virtual width is calculated by OpenCV, focal length is calculated above and known width is also explained above.(This formulae is derived by using Ray optics concepts.)
 ### Calculating Angles
 First we find the distance of `center of object` from the `center of screen` for the both the axis using formulae:
 
              X_virtual = -(center_x - scrnCenter_x)
              Y_virtual = -(center_y - scrnCenter_y)
          
 After calculating the X and Y distance from the center of screen. Then, using trignometric formulae `tan θ = Perpendicular / Base` for each axis. We find the angle of servos in Real Plane.
 
 ## Code Documentation
 ### Tracker.py
 
              port = '/dev/cu.usbserial-14230'
 
 set port for arduino from which arduino is connected to laptop/PC.
 
              serialcomm = serial.Serial(port, 9600, timeout=0.1)
              
 Connect to Arduino.
  
              HandDetector(detectionCon=0.8, maxHands=1)
           
  Hand detector function provided by cvzone librabry.
  
              focal_length = AvgFocalLength()
          
  Get average focal length of the camera.
  
              camera = cv.VideoCapture(1) 
              camera.set(cv.CAP_PROP_FRAME_WIDTH, screen_width)
              camera.set(cv.CAP_PROP_FRAME_HEIGHT, screen_height)
              
 Start capturing video and Sets screen_width and screen_height.
 
               ret, frame = camera.read()
               
 Return a boolean value and frame from the video.
 
              hands = detector.findHands(frame, draw=False)
              lmList = hands[0]['lmList']
              x, y, w, h = hands[0]['bbox']
              index_x, index_y, _ = lmList[5]      # X-Y co-ordinates for bottom of Index finger.
              pinky_x, pinky_y, _ = lmList[17]     # X-Y co-ordinates for bottom of Pinky finger.
              (center_x, center_y) = hands[0]['center']
              
 Detect hand in a given frame and return its X-Y co-ordinates, width, heigth, center co-ordinates, Index and Pinky finger co-ordinates of the detected hand.
 
               distance_virtual = (((pinky_x - index_x)**2) + ((pinky_y - index_y)**2))**(1/2)
               
Finds the virtual width of the object detected.

              Z_real = get_distance(focal_length, distance_virtual)
              
Get the distance of detected object from the camera.

              scrnCenter_x = screen_width/2
              scrnCenter_y = screen_height/2
              X_virtual = -(center_x - scrnCenter_x)
              Y_virtual = -(center_y - scrnCenter_y)
              X_real = X_virtual * correctionTerm
              Y_real = Y_virtual * correctionTerm
              
Finds the X and Y distance of onject center from the center of the screen.

                angles = Angles.turret(X_real, Y_real, Z_real)
                angles.offsets(-15, 10, -15)
                angles.getAngles()
                
Calculates the angle for the servos. The `offsets(x,y,z)` function sets the offsets values of the turret which means the difference in Turret X, Y, Z axis from the lens fo camera. Because the script calculates the angle from the center the center of the camera lens.

                motorX = "%" + "X" + str(int(angles.getTheta_x())) + "#"
                motorY = "%" + "Y" + str(int(angles.getTheta_y())) + "#"
                serialcomm.write(motorX.encode())
                serialcomm.write(motorY.encode())
                
 The above part of the code formats and send the angles to the arduino.
 ### Utils.py
 
                CalculateFocalLength((known_distance, known_width, virtual_width)
                
Calculate Focal length.

                get_distance(focal_length, virtual_width)
                
Calculates distance of object from the camera.

                AvgFocalLength()
                
Calculates average focal lengths.

### servo.ino

                servoX.attach(9);
                servoY.attach(10);
            
Attaches X axis servo to pin 9 and Y axis servo to pin 10.

                readSerial()
                
Read for serial input and call `on_receive()` function when input is received.

                on_receive()
                
 Deformat the received input and set servos to received angles.
 
 ## Steps to Implement:
 
 1. Install all library in `requirements.txt`.
 2. Connect Arduino and Webcam via USB Port.
 3. Run `Capture_ref_image.py` put your hand at `84cm` distance from the camera. Press `c` to capture series of image.
 4. Set Arduino port in `Tracker.py` and Execute `Tracker.py`.
 
