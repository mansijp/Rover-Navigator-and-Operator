from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import random
import logging
import hashlib
import requests
import os

app = FastAPI()

directions = ["N", "E", "S", "W"]
move = {"N": (-1, 0), "E": (0, 1), "S": (1, 0), "W": (0, -1)}

log_dir = os.path.join(os.path.dirname(__file__), "../views/static/logs")
if not os.path.exists(log_dir):
    os.makedirs(log_dir)
    
def get_logger(n):
    log_file = os.path.join(log_dir, f"logs_{n}.txt")
    logger = logging.getLogger(f"Rover_{n}")
    logger.setLevel(logging.DEBUG)
    
    file_handler = logging.FileHandler(log_file, mode='w')
    file_handler.setLevel(logging.DEBUG)
    
    logger.addHandler(file_handler)
    return logger
    
# Find PIN based on serial number
def find_pin(serial_num):
    counter = 0
    while True:
        # Validate the pin
        temp_mine_key = str(counter) + serial_num
        hash_val = hashlib.sha256(temp_mine_key.encode()).hexdigest()
            
        # Check if the hash value is valid
        if hash_val.startswith("000000"):
            result = (counter, serial_num, hash_val)
            return result
        counter += 1

# Share PIN with server
def share_mine_pin(pin, serial_num, hash_val):
    response = requests.post(f"http://127.0.0.1:8000/lab4/sharePin/{pin}/{serial_num}/{hash_val}")
    if response.status_code == 200:
        return True
    else:
        return False

# Move the rover according to commands
def run_commands(n, grid, rows, cols, mines_db):
    dir = "S"
    dug_a_mine = False
    status = "Finished"
    
    x, y = 0, 0    # face south and start at the top left
    rover_map = grid
    rover_map[x][y] = "*"     # initial location is visited

    logger = get_logger(n)
    logger.info(f">>>>> Beginning path traversal {n} <<<<<")
    
    response = requests.get(f"http://127.0.0.1:8000/lab4/rovers/{n}")
    commands = response.json().get('commands', "")
    
    for c in commands:
        if c == "L":
            dir = directions[(directions.index(dir) - 1) % 4]
        
        elif c == "R":
            dir = directions[(directions.index(dir) + 1) % 4]
        
        elif c == "D":
            shift_x, shift_y = move[dir]
            x2, y2 = x + shift_x, y + shift_y
                
            if x2 < 0 or x2 > (rows-1) or y2 < 0 or y2 > (cols-1):
                continue

            elif rover_map[x2][y2] == 1:
                # Check if the coordinates exist in the mines_db
                mine_key = f"{x2},{y2}"
                mine_to_decode = next((item for item in mines_db if mine_key == item), None)

                if mine_to_decode:
                    rover_serial_num = mines_db[mine_to_decode]
                    if not rover_serial_num:
                        return "Eliminated"
                    
                    # Find the PIN for this rover's mine
                    pin_result = find_pin(rover_serial_num)
                    
                    # Share the PIN with the server
                    pin_response = share_mine_pin(pin_result[0], pin_result[1], pin_result[2])
                    if pin_response:
                        logger.info(f"\nMINE DISARMED, PIN SAVED.\nPin: {pin_result[0]}, Serial Num: {pin_result[1]}\n")
                    
                    rover_map[x2][y2] = 0       # Mark the mine as dug (set the position to 0)
                    dug_a_mine = True           # Indicate that the current rover dug a mine

                else:
                    return f"Mine not found for coordinates: {x2},{y2}"

        elif c == "M":
            shift_x, shift_y = move[dir]
            x2, y2 = x + shift_x, y + shift_y
            
            if x2 < 0 or x2 > (rows-1) or y2 < 0 or y2 > (cols-1):
                continue
            elif rover_map[x2][y2] == 1 and not dug_a_mine:
                status = "Eliminated"
                break
            else:
                dug_a_mine = False
            
            x, y = x2, y2
            rover_map[x][y] = "*"
        
        # Log the command execution
        logger.info(f"Command executed: {c}\nRover Status: {status}\n\n")
    
    logger.info(f"Command executed: {c}\nRover Status: {status}")
    logger.info(f">>>>> Ending path traversal {n} <<<<<\n")
    
    path_file_path = os.path.join(os.path.dirname(__file__), f"../views/static/paths/path_{n}.txt")
    with open(path_file_path, "w") as file:
        for row in rover_map:
            file.write(" ".join(str(i) for i in row) + "\n")
    
    return status, x, y