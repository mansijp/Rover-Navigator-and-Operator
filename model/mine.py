from fastapi import FastAPI
from pydantic import BaseModel
from typing import Optional

app = FastAPI()

class Mine(BaseModel):
    mine_id: Optional[int] = None
    serial_number: str
    x: Optional[int] = None
    y: Optional[int] = None