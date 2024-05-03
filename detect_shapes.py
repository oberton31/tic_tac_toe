import cv2
import numpy as np
import time


board = [0, 0, 0, 0, 0, 0, 0, 0, 0]

def coord_to_pos(circle_center, board_center):
    variance = 20
    x, y = circle_center
    #print(x, y)
    center_x, center_y = board_center
    offset = 50
    if center_x - variance < x and center_x + variance > x \
        and center_y - variance < y and center_y + variance > y:
        return 4
    if center_x + offset - variance < x and center_x + offset + variance > x \
        and center_y - variance < y and center_y + variance > y:
        return 5
    elif center_x - offset - variance < x and center_x - offset + variance > x \
        and center_y - variance < y and center_y + variance > y:
        return 3
    elif center_x - offset - variance < x and center_x - offset + variance > x \
        and center_y + offset - variance < y and center_y + offset + variance > y:
        return 0
    elif center_x - variance < x and center_x + variance > x \
        and center_y + offset - variance < y and center_y + offset + variance > y:
        return 1
    elif center_x + offset - variance < x and center_x + offset + variance > x \
        and center_y + offset - variance < y and center_y + offset + variance > y:
        return 2
    elif center_x - offset - variance < x and center_x - offset + variance > x \
        and center_y - offset - variance < y and center_y - offset + variance > y:
        return 6
    elif center_x - variance < x and center_x + variance > x \
        and center_y - offset - variance < y and center_y - offset + variance > y:
        return 7
    elif center_x + offset - variance < x and center_x + offset + variance > x \
        and center_y - offset - variance < y and center_y - offset + variance > y:
        return 8
    else: return 10

def update_board(circle_center, board_center):
    pos = coord_to_pos(circle_center, board_center)
    if pos != 10 and board[pos] == 0:
        board[pos] = 1
        print(board)
        # calculate next move based on board
        # send machine to draw move

        # Make sure we  do not detect circles when there are not any there! Filter out some but need to be sure it is all

def find_shapes():
    camera = cv2.VideoCapture(0) # opening plugged in webcam
    circle_pos = []
    board_center = None

    # wait here for game to be started
    
    # when started, send signal to draw board, and have agent make first move if randomly chosen

    while board_center is None:
        ret, frame = camera.read()
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        edges = cv2.Canny(gray, 50, 150, apertureSize=3)

        # Find lines using Hough transform
        lines = cv2.HoughLinesP(edges, 1, np.pi/180, 100, minLineLength=50, maxLineGap=50)

        if lines is not None:
            # Collect endpoints of lines
            points = []
            for line in lines:
                x1, y1, x2, y2 = line[0]
                points.append((x1, y1))
                points.append((x2, y2))

            # Find unique points
            points = np.array(points)
            unique_points = np.unique(points, axis=0)

            # Filter lines based on angle
            filtered_lines = []
            for line in lines:
                x1, y1, x2, y2 = line[0]
                angle = np.arctan2(y2 - y1, x2 - x1) * 180 / np.pi
                # Exclude lines with angles outside a certain range
                if abs(angle) < 80 and abs(angle) > 10:
                    if x1 > 100 and x1 < frame.shape[1] - 100 and x2 > 100 and x2 < frame.shape[1] - 100 \
                                and y1 > 100 and y1 < frame.shape[0] - 100 and y2 > 100 and y2 < frame.shape[0] - 100:
                            filtered_lines.append(line)

            # If we have at least 5 unique points (4 corners + 1 intersection)
            if len(unique_points) >= 5:
                # Compute center of rectangle based on intersections
                rect_center = np.mean(unique_points, axis=0, dtype=int)
                if rect_center[0] > 200 and rect_center[0] < 300 \
                    and rect_center[1] > 175 and rect_center[1] < 250:
                    board_center = rect_center

                    # Draw center point
                    cv2.circle(frame, tuple(board_center), 5, (255, 0, 0), -1)

                # Display the image
                cv2.imshow('Center Rectangle', frame)

        cv2.waitKey(1)
    
    print(board_center)

    # after board is chosen, wait until new circle is detected
    # if new circle is detected, update board and have agent determine new move
    # draw new move

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
                        # play machine move
                    else:
                        for circle in circle_pos:
                            dist = np.hypot(np.float64(circle[0]) - np.float64(a), np.float64(circle[1]) - np.float64(b))
                            if dist < min_dist:
                                min_dist = dist
                            if min_dist < 10:
                                break
                        if min_dist >= 10:
                            update_board((a, b), board_center)
                            circle_pos.append((a, b))
                            # play machine move

                # Draw the circumference of the circle. 
                cv2.circle(frame, (a, b), r, (0, 255, 0), 2) 
            
                # Draw a small circle (of radius 1) to show the center. 
                cv2.circle(frame, (a, b), 1, (0, 0, 255), 3) 
        cv2.imshow("Detected Circle", frame) 
        cv2.waitKey(1)  # Add this line to refresh the window
        #print(circle_pos)


if __name__ == "__main__":
    find_shapes()
