from pydantic import BaseModel
from typing import List, Optional

class Map(BaseModel):
    rows: int
    cols: int
    data: Optional[List[List[int]]] = None 