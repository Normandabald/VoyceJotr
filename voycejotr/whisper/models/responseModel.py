from pydantic import BaseModel
from typing import Optional

class Response(BaseModel):
    id: Optional[int] = None
    text: str
    model: str
    time: float
    filename: Optional[str] = None