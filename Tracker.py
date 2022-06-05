import cv2 as cv
from cvzone.HandTrackingModule import HandDetector
from Utils import AvgFocalLength, get_distance
import Angles
import serial

screen_width = 1280
screen_height = 720

port = '/dev/cu.usbserial-14230'

serialcomm = serial.Serial(port, 9600, timeout=0.1)

detector = HandDetector(detectionCon=0.8, maxHands=1)

focal_length = AvgFocalLength()
print("Average: {}cm".format(focal_length))


camera = cv.VideoCapture(1) 
camera.set(cv.CAP_PROP_FRAME_WIDTH, screen_width)
camera.set(cv.CAP_PROP_FRAME_HEIGHT, screen_height)

while True:
    ret, frame = camera.read()

    hands = detector.findHands(frame, draw=False)

    if hands:
        lmList = hands[0]['lmList']
        x, y, w, h = hands[0]['bbox']
        index_x, index_y, _ = lmList[5]      # X-Y co-ordinates for bottom of Index finger.
        pinky_x, pinky_y, _ = lmList[17]     # X-Y co-ordinates for bottom of Pinky finger.
        (center_x, center_y) = hands[0]['center']    # Center of hand.

        # distance between Index and Pinky finger bottom in Image.
        distance_virtual = (((pinky_x - index_x)**2) +
                            ((pinky_y - index_y)**2))**(1/2)

        # Z-axis
        Z_real = get_distance(focal_length, distance_virtual)
        cv.putText(frame, f" Distance = {Z_real}",
                   (50, 50), cv.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 3)

        # X, Y-axis calculation
        correctionTerm = 6.3/distance_virtual # 6.3 is average distance between Index and Pinky finger.
        scrnCenter_x = screen_width/2
        scrnCenter_y = screen_height/2
        X_virtual = -(center_x - scrnCenter_x)
        Y_virtual = -(center_y - scrnCenter_y)
        X_real = X_virtual * correctionTerm
        Y_real = Y_virtual * correctionTerm

        # Printing on screen
        # cvzone.putTextRect(
        #     frame, f'{int(X_real)}cm {int(Y_real)}cm {int(Z_real)}cm', (x, y))
        cv.circle(frame, (640, 360), 2, (0, 0, 255), 2)
        cv.rectangle(frame, (x, y), (x+w, y+h), (0, 255, 0), 1)

        # Calculating servo angles
        angles = Angles.turret(X_real, Y_real, Z_real)
        angles.offsets(-15, 10, -15)
        angles.getAngles()

        motorX = "%" + "X" + str(int(angles.getTheta_x())) + "#"
        motorY = "%" + "Y" + str(int(angles.getTheta_y())) + "#"

        serialcomm.write(motorX.encode())
        serialcomm.write(motorY.encode())

    cv.imshow('frame', frame)

    if cv.waitKey(1) == ord('q'):
        break

camera.release()
cv.destroyAllWindows()
