#importing Modules
import cv2
import numpy as np
from getkey import getkey, keys
import time
import threading
from queue import Queue

q = Queue()


def play_video(): #function that plays a mp4 video file
    print('entering play video function')
    filePath = None
    while q.empty():
       pass
    filePath = q.get()
    cap = cv2.VideoCapture(filePath)
    print('filepath :' + filePath)
    while True:
        while q.empty():
            cap = cv2.VideoCapture(filePath)
            print('got the file')
            if cap.isOpened()== False:
                print("Oops! Error opening file.")

                #read until end of video
            while cap.isOpened() and q.empty():
                ret, frame = cap.read()
                if ret == True:
                    # Display the resulting frame
                    cv2.imshow('Frame', frame)
                    cv2.waitKey(1)

            if cap:
                 cap.release()
        filePath = q.get()
        print('filepath :' + filePath)


    cap.release()
    cv2.destroyAllWindows()



def play_visualEffect(first_color, second_color=None): # list all cases and play visual effects
    if first_color == "red":
        if second_color == "blue":
            print("play red+blue")
            q.put('movies/_red + blue.mp4')
        elif second_color == 'yellow':
            print('play red + yellow')
            q.put('movies/_red + yellow.mp4')
        else:
            print("play red")
            q.put('movies/_red.mp4')

    elif first_color == "blue":
        if second_color == "red":
            print("play blue+red")
            q.put('movies/_blue + red.mp4')
        elif second_color == "yellow":
            print("play blue + yellow")
            q.put('movies/_blue + yellow.mp4')
        else : #second color is yellow
            print("play blue")
            q.put('movies/_blue.mp4')

    else: #first color is yellow
        if second_color == "red":
            print("play yellow+red")
            q.put('movies/_yellow + red.mp4')
        elif second_color == "blue":
            print("play yellow+blue")
            q.put('movies/_yellow + blue.mp4')
        else:
            print("play yellow")#second color is yellow
            q.put('movies/_yellow.mp4')



def recognize_balls():
    first_color = None
    second_color = None
    blue_detected = False
    red_detected = False
    yellow_detected = False
    print("Welcome to the game!")
    # Capture video from webcam
    cam = cv2.VideoCapture(1)
    # ret, img = cam.read()
    if cam.isOpened():
        boolean, img = cam.read()
    else:
        boolean = False
    counter = 1
    while boolean:
        time.sleep(0.1)
        boolean, img = cam.read()

        if counter % 10 == 0:
            counter+=1
        else:
            counter+=1
            continue
        # if cv2.waitKey(20) == ord('r'):
        #     reset = True
        #     print "Reseting the game."




        #converting frame(img) from BGR (Blue-Green-Red) to HSV (hue-saturation-value)
        hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)

        lower_blue = np.array([110, 50, 50])
        upper_blue = np.array([130, 255, 255])
        mask_blue = cv2.inRange(hsv, lower_blue, upper_blue) # mask of blue
        img_blue = cv2.bitwise_and(hsv, hsv, mask = mask_blue) # filtered img of blue component

        lower_red = np.array([0, 70, 50])
        upper_red = np.array([10, 255, 255])
        mask1 = cv2.inRange(hsv, lower_red, upper_red)

        lower_red = np.array([170, 70, 50])
        upper_red = np.array([180, 255, 255])
        mask2 = cv2.inRange(hsv, lower_red, upper_red) #2 masks for 2 ranges of color red

        mask_red = mask1 + mask2 # join the masks
        img_red = cv2.bitwise_and(hsv, hsv, mask = mask_red) # filtered img of red component

        lower_yellow = np.array([20,100,100])
        upper_yellow = np.array([30,255,255])
        mask_yellow = cv2.inRange(hsv, lower_yellow, upper_yellow) # mask of yellow
        img_yellow = cv2.bitwise_and(hsv, hsv, mask = mask_yellow) # filtered img of yellow component


        # 2) morphological operations
        img_blue_processed = cv2.dilate(img_blue, None, iterations=2)
        img_blue_processed = cv2.erode(img_blue_processed, None, iterations=2)
        gray_img_blue = cv2.cvtColor(img_blue_processed, cv2.COLOR_BGR2GRAY) #converts the img to 1 channel

        img_red_processed = cv2.dilate(img_red, None, iterations=2)
        img_red_processed = cv2.erode(img_red_processed, None, iterations=2)
        gray_img_red = cv2.cvtColor(img_red_processed, cv2.COLOR_BGR2GRAY) #converts the img to 1 channel

        img_yellow_processed = cv2.dilate(img_yellow, None, iterations=2)
        img_yellow_processed = cv2.erode(img_yellow_processed, None, iterations=2)
        gray_img_yellow = cv2.cvtColor(img_yellow_processed, cv2.COLOR_BGR2GRAY) #converts the img to 1 channel


        # 3) contour detection
        contours_blue = cv2.findContours(gray_img_blue.copy(), cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)[-2]
        contours_blue = sorted(contours_blue, key=cv2.contourArea, reverse=True)

        contours_red = cv2.findContours(gray_img_red.copy(), cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)[-2]
        contours_red = sorted(contours_red, key=cv2.contourArea, reverse=True)

        contours_yellow = cv2.findContours(gray_img_yellow.copy(), cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)[-2]
        contours_yellow = sorted(contours_yellow, key=cv2.contourArea, reverse=True)


        #4) filtering contours by size
        contours = [contours_blue, contours_red, contours_yellow]
        for x in contours:
            if x:
                area = cv2.contourArea(x[0])
                rect = cv2.minAreaRect(x[0])
                entroid = (0,0)
                if area > 2000: #only coutours of the size of a t-shirt should be drawn out
                    #get coordinates of the centroid of the largest valid contour
                    box = cv2.boxPoints(rect)
                    pt_upperleft = box[0]
                    pt_lowerright = box[2]
                    center_x = (pt_upperleft[0] + pt_lowerright[0])/2
                    center_y = (pt_upperleft[1] + pt_lowerright[1])/2
                    centroid = (center_x, center_y) #This coordinate should be stored as a global variable. but where should it be declared?
                    box = np.int0(box)


                    #duration = time.time() - startTime

                    if True: #delay interval
                        if x == contours_blue:
                            cv2.drawContours(img, [box], 0, (0, 0, 255), 1) #draw out the contour in rectangle
                            cv2.putText(img, 'blue', (pt_upperleft[0], pt_upperleft[1]), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 0, 255), 1, cv2.LINE_AA)
                            blue_detected = True

                        if x == contours_red:
                            cv2.drawContours(img, [box], 0, (255, 0, 0), 1) #draw out the contour in rectangle
                            cv2.putText(img, 'red', (pt_upperleft[0], pt_upperleft[1]), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 0, 0), 1, cv2.LINE_AA)
                            red_detected = True

                        if x == contours_yellow:
                            cv2.drawContours(img, [box], 0, (180, 180, 0), 1) #draw out the contour in rectangle
                            cv2.putText(img, 'yellow', (pt_upperleft[0], pt_upperleft[1]), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (180, 180, 0), 1, cv2.LINE_AA)
                            yellow_detected = True

                        def get_color():  # get the current color
                            resultColor = None
                            if blue_detected:
                                resultColor = "blue"
                            if red_detected:
                                resultColor = "red"
                            if yellow_detected:
                                resultColor = "yellow"
                            return resultColor

                        def color_detected():  # returns true if a color is detected
                            return red_detected or blue_detected or yellow_detected

                        if red_detected or blue_detected or yellow_detected:
                            print("A ball is thrown in, processing...")

                            #color update
                            if not first_color and color_detected:
                                first_color = get_color()
                                print ("First color detected: " + first_color)
                                play_visualEffect(first_color)

                            elif first_color  and not second_color and color_detected:
                                second_color = get_color()
                                print("Second color detected: " + second_color)
                                play_visualEffect(first_color, second_color)

                            elif first_color and second_color and color_detected:
                                new_color = get_color()
                                first_color = second_color
                                second_color = new_color
                                print ("New color detected: " + new_color)
                                play_visualEffect(first_color, second_color)

                        blue_detected = False
                        red_detected = False
                        yellow_detected = False
                        print("Ready for another ball!")

        #cv2.namedWindow('webcam')
        #cv2.imshow('webcam', img)


thread1 = threading.Thread(target=recognize_balls)

thread1.start()

play_video()
