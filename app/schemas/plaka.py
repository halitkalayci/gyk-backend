from pydantic import BaseModel
from typing import List

class PlakaDetection(BaseModel):
    x1: float
    y1: float
    x2: float
    y2: float
    confidence: float

class PlakaResponse(BaseModel):
    detections: List[PlakaDetection]
    total_detections: int
    message: str
