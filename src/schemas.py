from typing import List

import orjson

from helpers.dataloading import BaseModel

# @dataclasses.dataclass
class Detection(BaseModel):
  id: int
  mac: str
  rssi: int
  uptime_ms: int
  battery: float
  detection_timestamp: int
  
  class Config:
    json_loads = orjson.loads

# @dataclasses.dataclass
class DataFile(BaseModel):
  detections: List[Detection]
  station_id: str

  class Config: 
    json_loads = orjson.loads