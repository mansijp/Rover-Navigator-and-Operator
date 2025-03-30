# Lab4-5: Rover Application

## Prerequisites
Ensure you have the following installed on your system:
- Python 3.10+
- `pip` (Python package manager)

## Setup Instructions

### 1 - Navigate to the Project Directory
Before running any commands, ensure you are inside the **`lab4`** directory:
```sh
cd lab4
```

### 2 - Install Dependencies and Virtual Environment
Run the following command to install all required Python libraries and virtual envrionment:
```sh
python -m venv venv
```
```sh
pip install -r requirements.txt
```


### 3 - Run the Application
Start the application by running:
```sh
python main.py
```

## Access the Application
Navigate to this link to access the application
- Development Environment
```sh
http://127.0.0.1:8000/lab4
```
- Deployed Environment
```sh
https://coe892lab42025g17-eubjf7asb2acbpdx.canadacentral-01.azurewebsites.net/lab4
```

## Project Structure
```
lab4/
│── main.py                # Entry point of the 
│── requirements.txt       # List of dependencies
│── Dockerfile             # Docker container setup
│── other_project_folders...
```

## Notes
- Make sure you are in the `lab4` directory before running any commands.
- If Python 3 is installed as `python3`, use `python3 main.py` instead.
- Use a python version `3.10` or above.

---