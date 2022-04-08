from dataclasses import dataclass, field
from typing import List, Dict

from schemas import Detection


@dataclass()
class Station:
    name: str
    ip: str
    db_port: str
    # To be populated by the application
    detections: List[Detection] = None

    def data_file(self) -> str:
        return f"data/6ul-{self.name}.dump.json"


config: List[Station] = [
    Station(name="ronny01", ip="172.19.0.9", db_port="6001"),
    Station(name="ronny02", ip="172.19.0.2", db_port="6002"),
    Station(name="ronny03", ip="172.19.0.3", db_port="6003"),
    Station(name="ronny04", ip="172.19.0.4", db_port="6004"),
    Station(name="ronny05", ip="172.19.0.5", db_port="6005"),
    Station(name="ronny06", ip="172.19.0.6", db_port="6006"),
    Station(name="ronny07", ip="172.19.0.7", db_port="6007"),
]
