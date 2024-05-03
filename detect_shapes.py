import cv2
import numpy as np
import time

def find_shapes():
    camera = cv2.VideoCapture(0) # opening plugged in webcam
    circle_pos = []
    while True:
        ret, frame = camera.read()

        # Convert to grayscale. 
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY) 
        
        # Blur using 3 * 3 kernel. 
        gray_blurred = cv2.blur(gray, (3, 3)) 
        
        # Apply Hough transform on the blurred image. 
        detected_circles = cv2.HoughCircles(gray_blurred,  
                        cv2.HOUGH_GRADIENT, 1, 20, param1 = 50, 
                    param2 = 30, minRadius = 1, maxRadius = 40) 
        
        # Draw circles that are detected. 
        if detected_circles is not None: 
        
            # Convert the circle parameters a, b and r to integers. 
            detected_circles = np.uint64(np.around(detected_circles)) 
        
            for pt in detected_circles[0, :]: 
                a, b, r = pt[0], pt[1], pt[2] 
                min_dist = float('inf')
                
                # Check if (a, b) is already in circle_pos
                if not any((a, b) == pos for pos in circle_pos):
                    if not circle_pos:
                        circle_pos.append((a, b))
                    else:
                        for circle in circle_pos:
                            dist = np.hypot(circle[0] - a, circle[1] - b)
                            if dist < min_dist:
                                min_dist = dist
                            if min_dist < 50:
                                break
                        
                        if min_dist >= 50:
                            circle_pos.append((a, b))
                # Draw the circumference of the circle. 
                cv2.circle(frame, (a, b), r, (0, 255, 0), 2) 
            
                # Draw a small circle (of radius 1) to show the center. 
                cv2.circle(frame, (a, b), 1, (0, 0, 255), 3) 
        print(circle_pos)
        cv2.imshow("Detected Circle", frame) 
        cv2.waitKey(1)  # Add this line to refresh the window
        #print(circle_pos)
        #time.sleep(5)

if __name__ == "__main__":
    find_shapes()
