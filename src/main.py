from timeit import default_timer as timer
from time import sleep, time

from datetime import datetime, timedelta
from typing import List, Optional
from pydantic import BaseModel as PydanticBaseModel
import json

import dataclasses, orjson, typing

def td_format(td_object):
    seconds = int(td_object.total_seconds())
    periods = [
        ('year',        60*60*24*365),
        ('month',       60*60*24*30),
        ('day',         60*60*24),
        ('hour',        60*60),
        ('minute',      60),
        ('second',      1)
    ]

    strings=[]
    for period_name, period_seconds in periods:
        if seconds > period_seconds:
            period_value , seconds = divmod(seconds, period_seconds)
            has_s = 's' if period_value > 1 else ''
            strings.append("%s %s%s" % (period_value, period_name, has_s))

    return ", ".join(strings)


# https://github.com/samuelcolvin/pydantic/issues/1168
# Loading nested data without validation is not supported in the lib
class BaseModel(PydanticBaseModel):
    @classmethod
    def construct(cls, _fields_set=None, **values):

        m = cls.__new__(cls)
        fields_values = {}

        for name, field in cls.__fields__.items():
            key = field.alias  # this is the current behaviour of `__init__` by default
            if key:
                if issubclass(field.type_, BaseModel):
                    if field.shape == 2:  # the field is a `list`. You could check other shapes to handle `tuple`, ...
                        fields_values[name] = [
                            field.type_.construct(**e)
                            for e in values[key]
                        ]
                    else:
                        fields_values[name] = field.outer_type_.construct(**values[key])
                else:
                    if values[key] is None and not field.required:
                        fields_values[name] = field.get_default()
                    else:
                        fields_values[name] = values[key]
            elif not field.required:
                fields_values[name] = field.get_default()

        object.__setattr__(m, '__dict__', fields_values)
        if _fields_set is None:
            _fields_set = set(values.keys())
        object.__setattr__(m, '__fields_set__', _fields_set)
        m._init_private_attributes()
        return m



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

def process(datas):
  for data in datas:
    print(f"{data.station_id}: {len(data.detections)} detections")
    in_order = True
    last_time = None
    for detection in data.detections:
      if last_time == None:
        last_time = detection.detection_timestamp
      else:
        if last_time > detection.detection_timestamp:
          print("Detection our of order")
          print(detection)
          exit(1)
      last_time = detection.detection_timestamp
    print(f"{data.station_id}: Detections in order")

    print()

    earliest_detection = min([data.detections[0].detection_timestamp for data in datas])
    print(f" * Race was at \t\t {datetime.utcfromtimestamp(earliest_detection).strftime('%Y-%m-%d %H:%M:%S')}")

    start_time = time()
    pretty_start_time = datetime.utcfromtimestamp(start_time).strftime('%Y-%m-%d %H:%M:%S')
    print(f" * Mocking starting at \t {pretty_start_time}")

    time_diff = start_time - earliest_detection
    pretty_time_diff = td_format(timedelta(seconds=time_diff))
    print(f" * Starting with a diff of {pretty_time_diff}")
    print()

    sleep(1)
    cursors = [0 for station_data in datas]
    glob_i = 0
    
    did_process = False
    while(True):
      now = time()
      local_i = 0

      for i, cursor in enumerate(cursors):
        if cursor >= len(datas[i].detections): continue

        did_process = True
        detection_time = datas[i].detections[cursor].detection_timestamp
        while detection_time + time_diff < now:
          print(f"{glob_i}: {datas[i].detections[cursor]}")
          glob_i += 1
          local_i += 1
          cursor += 1

          detection_time = datas[i].detections[cursor].detection_timestamp
        cursors[i] = cursor

      if did_process:
        did_process = False

        if local_i > 0:
          since_local_start = now - start_time
          pretty_time_diff = td_format(timedelta(seconds=since_local_start))
          print(f"{pretty_time_diff} in the race.\tSent {local_i} detections.")
        sleep(0.1)
      else:
        break
    

def main():
  start = timer()
  data_files = [f"data/ronny0{i}.dump.json" for i in range(1,6)]
  data = []
  for data_file in data_files:
    with open(data_file, "rb") as f:
      data_dict = orjson.loads(f.read())
      # use construct to skip validation, we have data from a trusted source
      data_obj = DataFile.construct(**data_dict)
      data.append(data_obj)

  end = timer()
  print("Took {:.2f} s to load all data".format(end - start))

  process(data)

if __name__ == "__main__":
  main()
