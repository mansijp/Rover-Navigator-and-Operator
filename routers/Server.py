from fastapi import APIRouter, HTTPException, Body
from fastapi.templating import Jinja2Templates
from random import randint
import requests, json, hashlib, os
from controller.rover_client import *
from model.map import *
from model.mine import *
from model.rover import *
from typing import Tuple

base_dir = os.path.dirname(os.path.abspath(__file__))
templates_dir = os.path.join(base_dir, "..", "views", "templates")
templates = Jinja2Templates(directory=templates_dir)

router = APIRouter()

# Database for storing rovers and mines
rovers_db = {}
mines_db = {}
map_db = {}
commands_db = {}


@router.get("/commands/{n}")        # works
def get_commands(n: int):
    commands = requests.get(f"https://coe892.reev.dev/lab1/rover/{n}")
    data = commands.json()
    moves = data['data']['moves']
    return moves


@router.get('/map/size', response_model=Tuple[int, int])
def get_map_size():
    map_file_path = os.path.join(os.path.dirname(__file__), "../views/static/map.txt")
    with open(map_file_path, "r") as file:
        rows, cols = map(int, file.readline().split())
    return (rows, cols)

@router.get('/map')
def getMap():
    grid = []
    
    mine_file_path = os.path.join(os.path.dirname(__file__), "../views/static/mines.txt")
    
    with open(mine_file_path, "r") as file:
        mines = []
        for index, line in enumerate(file, start=1):
            serial_number = line.strip()
            mines.append(serial_number)  

    assigned_mines = set()

    map_file_path = os.path.join(os.path.dirname(__file__), "../views/static/map.txt")
    with open(map_file_path, "r") as file:
        rows, cols = map(int, file.readline().split())
        for r, line in enumerate(file):
            values = list(map(int, line.split()))
            for c, value in enumerate(values):
                if value == 1:  
                    if f"{r},{c}" not in mines_db:  
                        available_mines = list(set(mines) - assigned_mines)
                        if available_mines:
                            serial = random.choice(available_mines)
                            assigned_mines.add(serial) 
                            mines_db[f"{r},{c}"] = serial 
            grid.append(values)
    
    map_db = {"rows": rows, "cols": cols, "data": grid, "mines_db": mines_db}
    return map_db


@router.get("/map/grid/{rover_id}", response_model=List[List[str]])
def get_map_grid(rover_id: int):
    rover_file_path = os.path.join(os.path.dirname(__file__), f"../views/static/rovers.txt")
    map_file_path = os.path.join(os.path.dirname(__file__), f"../views/static/paths/path_{rover_id}.txt")

    with open(rover_file_path, "r") as file:
        lines = file.readlines()
    if rover_id < 1 or rover_id > len(lines):
        raise HTTPException(status_code=404, detail="Rover not found")
    
    with open(map_file_path, "r") as file:
        lines = file.readlines()
    map_grid = [line.strip().split() for line in lines]
    
    return map_grid

    
@router.put('/map')
def updateMap(map: Map):
    rows = map.rows
    cols = map.cols
    map_data = getMap()['data']  # Fetch the current map data
    current_rows = len(map_data)
    current_cols = len(map_data[0]) if current_rows > 0 else 0

    # Add padding if rows are increased (at the bottom)
    if rows > current_rows:
        for _ in range(rows - current_rows):
            map_data.append([0] * current_cols)  # Add zero-filled rows at the bottom

    # Add padding if cols are increased (at the right)
    if cols > current_cols:
        for i in range(len(map_data)):
            map_data[i].extend([0] * (cols - current_cols))  # Add zeroes at the end of each row

    # Remove rows if needed
    if rows < current_rows:
        map_data = map_data[:rows]  # Trim rows if rows are reduced

    # Remove columns if needed
    if cols < current_cols:
        for i in range(len(map_data)):
            map_data[i] = map_data[i][:cols]  # Trim columns if columns are reduced

    # Write the updated map to the file
    map_file_path = os.path.join(os.path.dirname(__file__), "../views/static/map.txt")
    with open(map_file_path, "w") as file:
        file.write(f"{rows} {cols}\n")
        for row in map_data:
            file.write(" ".join(str(x) for x in row) + "\n")

    return {"rows": rows, "cols": cols, "data": map_data}


# Mine functions



@router.get('/mines', response_model=List[Mine])
def getMines():
    mines = []
    mine_file_path = os.path.join(os.path.dirname(__file__), "../views/static/mines.txt")
    with open(mine_file_path, "r") as file:
        for index, line in enumerate(file, start=1):
            serial_number = line.strip()
            mine = Mine(mine_id=index, serial_number=serial_number)
            
            for coords, serial in mines_db.items():
                if serial_number == serial:
                    x, y = map(int, coords.split(','))
                    mine.x = x
                    mine.y = y
                    break
            mines.append(mine)
    return mines


@router.get('/mines/{mine_id}', response_model=Mine)  # Ensure to use response_model for proper serialization
def getMineById(mine_id: int):
    mines = getMines()  # Assuming getMines() returns a list of mine objects
    if mine_id < 1 or mine_id > len(mines):
        raise HTTPException(status_code=404, detail="Mine not found")
    print(mines[mine_id - 1])
    return mines[mine_id - 1]  # Return the specific mine object, not just the serial number


@router.delete('/mines/{mine_id}')
def deleteMineById(mine_id: int):
    mines = getMines()
    if mine_id < 1 or mine_id > len(mines):
        raise HTTPException(status_code=404, detail="Mine not found")
    
    mine_file_path = os.path.join(os.path.dirname(__file__), "../views/static/mines.txt")
    map_file_path = os.path.join(os.path.dirname(__file__), "../views/static/map.txt")
    
    with open(mine_file_path, "r") as file:
        lines = file.readlines()
    
    mine_to_delete = lines[mine_id - 1].strip()
    deleted_mine = {"mine_id": mine_id, "serial_number": mine_to_delete}
    mine_coordinates = None
    for coord, serial in mines_db.items():
        if serial == mine_to_delete:
            mine_coordinates = coord
            break
    
    if mine_coordinates:
        x, y = map(int, mine_coordinates.split(','))
        with open(map_file_path, "r") as file:
            map_lines = file.readlines()
        line = map_lines[x + 1].strip()
        map_lines[x + 1] = map_lines[x + 1][:y * 2] + '0' + map_lines[x + 1][y * 2 + 1:]
        with open(map_file_path, "w") as file:
            file.writelines(map_lines)
        del mines_db[mine_coordinates]
        
    with open(mine_file_path, "w") as file:
        for line in lines:
            if line.strip() != mine_to_delete:
                file.write(line)

    return {"message": f"Mine with serial number {mine_to_delete} has been successfully deleted", "deleted_mine": deleted_mine}


@router.post("/mines")
def createMine(mine: Mine):
    mine_file_path = os.path.join(os.path.dirname(__file__), "../views/static/mines.txt")
    map_file_path = os.path.join(os.path.dirname(__file__), "../views/static/map.txt")
    
    with open(mine_file_path, "r") as file:
        lines = file.readlines()
    mine_id = len(lines) + 1
    with open(mine_file_path, "a") as file:
        file.write(f"{mine.serial_number}\n")
    with open(map_file_path, "r") as file:
        map_lines = file.readlines()
    
    map_rows = int((map_lines[0].split())[0])
    map_cols = int((map_lines[0].split())[1])
    
    if 0 <= mine.x < map_rows and 0 <= mine.y < map_cols and (mine.x != 0 and mine.y != 0):
        mine.x += 1
        line = map_lines[mine.x].strip()
        if line[mine.y * 2] != '1':
            map_lines[mine.x] = map_lines[mine.x][:mine.y * 2] + '1' + map_lines[mine.x][mine.y * 2 + 1:]
            mine.x -= 1
            mines_db[f"{mine.x},{mine.y}"] = mine.serial_number
            
            with open(map_file_path, "w") as file:
                file.writelines(map_lines)

    return {"mine_id": mine_id, "x": mine.x, "y": mine.y, "message": "Mine successfully created"}

@router.put('/mines/{mine_id}')     # works
def updateMineById(mine_id: int, serial_number: str = None):
    mine_file_path = os.path.join(os.path.dirname(__file__), "../views/static/mines.txt")
    with open(mine_file_path, "r") as file:
        lines = file.readlines()
    if mine_id < 1 or mine_id > len(lines):
        raise HTTPException(status_code=404, detail="Mine not found")
    
    mine_data = lines[mine_id - 1].strip()
    original_mine_data = mine_data

    if serial_number:
        mine_data = serial_number
    if serial_number:
        lines[mine_id - 1] = mine_data + "\n"
        with open(mine_file_path, "w") as file:
            file.writelines(lines)
        return {"mine_id": mine_id, "serial_number": mine_data, "message": "Mine successfully updated"}
    
    return {"mine_id": mine_id, "serial_number": original_mine_data, "message": "No updates provided, returning original mine"}


# Rover functions


@router.get('/rovers/reset')        # works
def resetRovers():
    rovers_file_path = os.path.join(os.path.dirname(__file__), "../views/static/rovers.txt")
    rovers = []
    updated_lines = []

    for index in range(1, 11):
        status = "Not_Started"
        commands = get_commands(index)
        rovers.append({"id": str(index), "status": status, "commands": commands})
        updated_lines.append(f"{index} {status} {commands}\n")

    with open(rovers_file_path, "w") as file:
        file.writelines(updated_lines)

    return {"rovers": rovers, "message": "All rovers are reset to their original states!"}


@router.get('/rovers', response_model=List[Rover])  # Specify the response model as List[Rover]
def getRovers():
    rovers_file_path = os.path.join(os.path.dirname(__file__), "../views/static/rovers.txt")
    rovers = [] 
    with open(rovers_file_path, "r") as file:
        lines = file.readlines()
    
    for index, line in enumerate(lines, start=1):
        line_data = line.strip().split(" ", 2)
        rover_id = index  # Use integer type for rover_id
        status = line_data[1] if len(line_data) > 1 else "Not_Started"
        commands = line_data[2] if len(line_data) > 2 else ""   
        rovers.append(Rover(rover_id=rover_id, status=status, commands=commands))  # Create Rover instance
    
    return rovers


@router.get('/rovers/{rover_id}')       # works
def get_rover_by_id(rover_id: int):
    rovers_file_path = os.path.join(os.path.dirname(__file__), "../views/static/rovers.txt")
    with open(rovers_file_path, "r") as file:
        lines = file.readlines()
    
    if rover_id < 1 or rover_id > len(lines):
        raise HTTPException(status_code=404, detail="Rover not found")
    rover_data = lines[rover_id - 1].strip()
    rover_status = rover_data.split(" ")[1]
    rover_commands = rover_data.split(" ")[2]
    
    return {"rover_id": rover_id, "status": rover_status, "commands": rover_commands}

@router.post('/rovers')
def createRover(rover: Rover):
    rover_file_path = os.path.join(os.path.dirname(__file__), "../views/static/rovers.txt")
    line_number = len(open(rover_file_path).readlines()) + 1
    new_rover = Rover(rover_id=line_number, status="Not_Started", commands=rover.commands)
    with open(rover_file_path, "a") as file:
        file.write(f"{new_rover.rover_id} {new_rover.status} {new_rover.commands}\n")
    return {"rover_id": new_rover.rover_id, "commands": new_rover.commands, "status": new_rover.status, "message": "Rover successfully created"}


@router.delete('/rovers/{rover_id}')    # works
def deleteRover(rover_id: int):
    rovers_file_path = os.path.join(os.path.dirname(__file__), "../views/static/rovers.txt")
    with open(rovers_file_path, "r") as file:
        lines = file.readlines()
    if rover_id < 1 or rover_id > len(lines):
        raise HTTPException(status_code=404, detail="Rover not found")

    del lines[rover_id - 1]
    with open(rovers_file_path, "w") as file:
        file.writelines(lines)

    return {"message": f"Rover {rover_id} has been successfully deleted"}


@router.put('/rovers/{rover_id}')
def updateRover(rover_id: int, commands: str = Body(..., embed=True)):
    rovers_file_path = os.path.join(os.path.dirname(__file__), "../views/static/rovers.txt")
    with open(rovers_file_path, "r") as file:
        lines = file.readlines()

    if rover_id < 1 or rover_id > len(lines):
        raise HTTPException(status_code=404, detail="Rover not found")
    line_data = lines[rover_id - 1].strip().split(" ", 2)
    rover_status = line_data[1]

    if rover_status not in ["Not_Started", "Finished"]:
        raise HTTPException(status_code=405, detail="Rover is active or eliminated")
    lines[rover_id - 1] = f"{line_data[0]} {rover_status} {commands}\n"
    with open(rovers_file_path, "w") as file:
        file.writelines(lines)

    return {"message": f"Rover {rover_id} updated successfully.", "commands": commands}


@router.post('/rovers/{rover_id}/dispatch')
def dispatchRover(rover_id: int):
    rovers_file_path = os.path.join(os.path.dirname(__file__), "../views/static/rovers.txt")

    with open(rovers_file_path, "r") as file:
        lines = file.readlines()
    if rover_id < 1 or rover_id > len(lines):
        raise HTTPException(status_code=404, detail="Rover not found")
    line_data = lines[rover_id - 1].strip().split(" ", 2)
    if len(line_data) < 3:
        raise HTTPException(status_code=400, detail="Invalid rover data format")

    status, commands = line_data[1], line_data[2]

    if status not in ["Not_Started", "Finished"]:
        raise HTTPException(status_code=405, detail="Rover cannot be dispatched in its current state")

    rows, cols, grid = getMap()['rows'], getMap()['cols'], getMap()['data'] 
    final_status, x, y = run_commands(rover_id, grid, rows, cols, mines_db)
    
    # Update the status of the rover in the file
    rovers_file_path = os.path.join(os.path.dirname(__file__), "../views/static/rovers.txt")
    with open(rovers_file_path, "r") as file:
        lines = file.readlines()

    if rover_id < 1 or rover_id > len(lines):
        raise HTTPException(status_code=404, detail="Rover not found")
    line_data = lines[rover_id - 1].strip().split(" ", 2)
    rover_status = line_data[1]

    if rover_status not in ["Not_Started", "Finished"]:
        raise HTTPException(status_code=405, detail="Rover is active or eliminated")
    lines[rover_id - 1] = f"{line_data[0]} {final_status} {commands}\n"
    with open(rovers_file_path, "w") as file:
        file.writelines(lines)

    # Return result
    return {"id": rover_id, "status": final_status, "xPos": x, "yPos": y, "commands": commands}


# Pins file and management


@router.post("/sharePin/{pin}/{serial_num}/{hash_val}")
def savePin(pin: str, serial_num: str, hash_val: str):    
    try:
        PINS_FILE_PATH = os.path.join(os.path.dirname(__file__), "../views/static/pins.txt")
        with open(PINS_FILE_PATH, "a") as file:
            file.write(f"{pin} {serial_num} {hash_val}\n")
        return True
    except Exception as e:
        return False

# Handling sending logs

@router.get("/logs/{rover_id}")
def get_logs(rover_id: int):
    log_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "../views/static/logs"))
    log_file_path = os.path.join(log_dir, f"logs_{rover_id}.txt")
    if not os.path.exists(log_file_path):
        raise HTTPException(status_code=404, detail=f"Logs not found for rover {rover_id}")
    with open(log_file_path, "r") as file:
        logs = file.read()
    
    return logs