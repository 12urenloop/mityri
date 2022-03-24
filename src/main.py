from timeit import default_timer as timer
from time import sleep, time

from datetime import datetime, timedelta
from typing import List, Optional
import json

import dataclasses, orjson, typing, psycopg2

from helpers.formatters import td_format
from schemas import DataFile, Detection

from config import config

def insert_detection(station, detection):
  # Save a detection in the db
  conn = None
  try:
    conn = psycopg2.connect(f"postgresql://postgres:postgres@{station.ip}:5432/ronny")
    cur = conn.cursor()
    cur.execute("""INSERT into detection(
      detection_time, mac, rssi, baton_uptime_ms, battery_percentage)
      VALUES (%s, %s, %s, %s, %s)""", (
        detection.detection_timestamp, 
        detection.mac, detection.rssi,
        detection.uptime_ms, 
        detection.battery))
    conn.commit()
    cur.close()
    conn.close()
  except (Exception, psycopg2.DatabaseError) as error:
    print(error)
  finally:
    if conn is not None:
      conn.close()


def process(stations):
  for station in stations:
    print(f"{station.name}: {len(station.detections)} detections")
    in_order = True
    last_time = None
    for detection in station.detections:
      if last_time == None:
        last_time = detection.detection_timestamp
      else:
        if last_time > detection.detection_timestamp:
          print("Detection our of order")
          print(detection)
          exit(1)
      last_time = detection.detection_timestamp
    print(f"{station.name}: Detections in order")

    print()

  earliest_detection = min([station.detections[0].detection_timestamp for station in stations])
  print(f" * Race was at \t\t {datetime.utcfromtimestamp(earliest_detection).strftime('%Y-%m-%d %H:%M:%S')}")

  start_time = time()
  pretty_start_time = datetime.utcfromtimestamp(start_time).strftime('%Y-%m-%d %H:%M:%S')
  print(f" * Mocking starting at \t {pretty_start_time}")

  time_diff = start_time - earliest_detection
  pretty_time_diff = td_format(timedelta(seconds=time_diff))
  print(f" * Starting with a diff of {pretty_time_diff}")
  print()

  sleep(1)
  cursors = [0 for _ in range(len(stations))]
  glob_i = 0
  
  did_process = False
  while(True):
    now = time()
    local_i = 0

    for i, cursor in enumerate(cursors):
      if cursor >= len(stations[i].detections): continue

      did_process = True
      detection = stations[i].detections[cursor]
      detection_time = detection.detection_timestamp
      while detection_time + time_diff < now:
        # insert_detection(station, detection)
        print(f"{glob_i}: {stations[i].detections[cursor]}")
        glob_i += 1
        local_i += 1
        cursor += 1

        detection_time = stations[i].detections[cursor].detection_timestamp
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
  for station in config:
    with open(station.data_file(), "rb") as f:
      data_dict = orjson.loads(f.read())
      # use construct to skip validation, we have data from a trusted source
      data_obj = DataFile.construct(**data_dict)
      if data_obj.station_id != station.name:
        print("Datafile - Config mismatch. {station.data_file()} has id: {data_obj.station_id} but the config has {station.name}")
        exit(1)
  
      station.detections = data_obj.detections
      data.append(station)

  end = timer()
  print("Took {:.2f} s to load all data".format(end - start))

  process(data)

if __name__ == "__main__":
  main()
