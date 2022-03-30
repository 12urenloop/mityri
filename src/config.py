from dataclasses import dataclass, field
from typing import List, Dict

from schemas import Detection

@dataclass()
class Station():
    name: str
    ip: str
    # To be populated by the application
    detections: List[Detection] = None

    def data_file(self) -> str:
        return f"data/{self.name}.dump.json"

config: List[Station] = [
    Station(name = "ronny01", ip="172.12.50.101"),
    #Station(name = "ronny02", ip="172.19.0.2"),
    #Station(name = "ronny03", ip="172.19.0.3"),
    #Station(name = "ronny04", ip="172.19.0.4"),
    #Station(name = "ronny05", ip="172.19.0.5"),
    # Station(name = "ronny06", ip="172.19.0.6"),
]
