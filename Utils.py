import cv2
import os
from cvzone.HandTrackingModule import HandDetector

# Variables
Known_distance = 84        # in cm
Known_width = 6.3        # in cm
number_of_images = 51
focal_lengths = []
Dir_name = "capture_images"

detector = HandDetector(detectionCon=0.8, maxHands=1)


def CalculateFocalLength(known_distance, known_width, virtual_width):
    focal_length = (virtual_width * known_distance)/known_width
    return focal_length


def Hand_Detection(image):
    hand_width = 0
    hands = detector.findHands(image, draw=False)
    if hands:
        lmList = hands[0]['lmList']
        index_x, index_y, _ = lmList[5]
        pinky_x, pinky_y, _ = lmList[17]
        hand_width = (((pinky_x - index_x)**2) +
                      ((pinky_y - index_y)**2))**(1/2)
    return hand_width


def Average(list):
    return sum(list) / len(list)


def AvgFocalLength():
    IsDirExist = os.path.exists(Dir_name)

    if IsDirExist == False:
        print("NO FOLDER NAMED capture_images FOUND!!!")
        exit(0)

    for i in range(number_of_images):
        image_name = "frame-{}.png".format(i+1)
        reference_image = cv2.imread(f"{Dir_name}/{image_name}")
        Virtual_width = Hand_Detection(reference_image)

        calculated_focal_length = CalculateFocalLength(
            Known_distance, Known_width, Virtual_width)

        if abs(calculated_focal_length) != 0:
            focal_lengths.append(calculated_focal_length)

    print(focal_lengths)
    return round(Average(focal_lengths), 2)


def get_distance(focal_length, virtual_width):
    distance = (Known_width * focal_length)/virtual_width
    return distance
