import cv2
import numpy as np
from minimax import findBestMove
import serial
import time
from gpiozero import Button

board = [['_', '_', '_'], ['_', '_', '_'], ['_', '_', '_']]
player, opponent = 'x', 'o' 

ser = serial.Serial('/dev/ttyACM0', 9600, timeout=1)

button = Button(4)

def send_message(message):
    ser.write(message.encode('utf-8'))
    while True:
        time.sleep(0.5)
        if (ser.in_waiting > 0):
            msg = ser.readline().decode('utf-8').rstrip()
            if msg == 'done': break

def coord_to_pos(circle_center, board_center):
    variance = 20
    x, y = circle_center
    center_x, center_y = board_center
    offset = 50

    # 0, 0 point is top left of image
    if center_x - variance < x and center_x + variance > x \
        and center_y - variance < y and center_y + variance > y:
        return 1, 1
    if center_x + offset - variance < x and center_x + offset + variance > x \
        and center_y - variance < y and center_y + variance > y:
        return 1, 2
    elif center_x - offset - variance < x and center_x - offset + variance > x \
        and center_y - variance < y and center_y + variance > y:
        return 1, 0
    elif center_x - offset - variance < x and center_x - offset + variance > x \
        and center_y - offset - variance < y and center_y - offset + variance > y:
        return 0, 0, 0
    elif center_x - variance < x and center_x + variance > x \
        and center_y - offset - variance < y and center_y - offset + variance > y:
        return 0, 1
    elif center_x + offset - variance < x and center_x + offset + variance > x \
        and center_y - offset - variance < y and center_y - offset + variance > y:
        return 0, 2
    elif center_x - offset - variance < x and center_x - offset + variance > x \
        and center_y + offset - variance < y and center_y + offset + variance > y:
        return 2, 0
    elif center_x - variance < x and center_x + variance > x \
        and center_y + offset - variance < y and center_y + offset + variance > y:
        return 2, 1
    elif center_x + offset - variance < x and center_x + offset + variance > x \
        and center_y + offset - variance < y and center_y + offset + variance > y:
        return 2, 2
    else: return 10, 10


def end_game(b):
    for row in range(3) :      
        if (b[row][0] == b[row][1] and b[row][1] == b[row][2]) :   
            return True, row       
  
    # Checking for Columns for X or O victory.  
    for col in range(3) : 
        if (b[0][col] == b[1][col] and b[1][col] == b[2][col]) : 
            return True, col + 3
  
    # Checking for Diagonals for X or O victory.  
    if (b[0][0] == b[1][1] and b[1][1] == b[2][2]) : 
        return True, 6

  
    if (b[0][2] == b[1][1] and b[1][1] == b[2][0]) : 
        return True, 7
  
    
    for row in range(3):
        for col in range(4):
            if b[row][col] == '_':
                return False, None
    return True, 8 # return tie

def update_board(circle_center, board_center):
    i, j= coord_to_pos(circle_center, board_center)
    if (i, j) != (10, 10) and board[i][j] == '_':
        board[i][j] = opponent
        game_over, winning_combo = end_game(board)
        if game_over:
            send_message(f"win {winning_combo}\n")
            return True
        time.sleep(5)
        row, col, move_no = findBestMove(board)
        board[row][col] = player
        game_over, winning_combo = end_game(board)
        if game_over:
            send_message(f"mov {move_no}\n")
            send_message(f"win {winning_combo}\n")
            return True
        else:
            send_message(f"mov {move_no}")
            send_message("return\n")
            return False



def play_game():
    camera = cv2.VideoCapture(0) # opening plugged in webcam
    #circle_pos = []
    board_center = None

    # on boot, zero device and move to ready position
    
    # Wait until arduino is ready to send/recieve messages
    ser.flush()
    while True:

        if (ser.in_waiting > 0):
            msg = ser.readline().decode('utf-8').rstrip() #  pull message from buffer
            ser.write("ready\n".encode('utf-8')) 
            # arduino now  homes and moves to out of way position
            break 
    ser.flush()
    
    while True:
        # wait for button press

        while not button.is_pressed:
            pass
    

        board = [['_', '_', '_'], ['_', '_', '_'], ['_', '_', '_']]

        # draw board
        send_message("start\n")
        
        start_move = np.random.randint(2)
        if start_move == 0:
            row, col, move_no = findBestMove(board)
            board[row][col] = player
            send_message(f"mov {move_no}\n")
        send_message("return\n")

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
        done = False
        while not done:
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
                    done = update_board((a, b), board_center)

                    # Draw the circumference of the circle. 
                    #cv2.circle(frame, (a, b), r, (0, 255, 0), 2) 
                
                    # Draw a small circle (of radius 1) to show the center. 
                    #cv2.circle(frame, (a, b), 1, (0, 0, 255), 3) 
            cv2.imshow("Detected Circle", frame) 
            cv2.waitKey(1)  # Add this line to refresh the window
        #  game is over, wait to start new instance


if __name__ == "__main__":
    play_game()

            
    
