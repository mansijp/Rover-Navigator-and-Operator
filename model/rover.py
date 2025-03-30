from fastapi import FastAPI
from pydantic import BaseModel
from typing import Optional

app = FastAPI()

class Rover(BaseModel):
    rover_id: Optional[int] = None
    status: Optional[str] = "Not_Started"
    commands: str