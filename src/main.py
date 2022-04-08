from timeit import default_timer as timer
from time import sleep, time, mktime

from datetime import datetime, timedelta
from typing import List, Optional
import json

import dataclasses, orjson, typing

from helpers.formatters import td_format
from schemas import DataFile, Detection
from database import run_query
from config import config

MOCK_REPLAY_SPEED = 10

START_MOCK_DATETIME = datetime(2022, 3, 31, 17, 30, 00)

def insert_detection(station, detection):
    dt_object = datetime.fromtimestamp(detection.detection_timestamp)
    # .strftime(
    #     "%Y-%m-%d %H:%M:%S"
    # )
    run_query(
        station,
        """INSERT into detection(
      detection_time, mac, rssi, baton_uptime_ms, battery_percentage)
      VALUES (%s, %s, %s, %s, %s)""",
        (
            dt_object,
            detection.mac,
            detection.rssi,
            detection.uptime_ms,
            detection.battery,
        ),
    )


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
                    pass
                    # print("Detection out of order")
                    # print(f"  Station: {station.name}")
                    # print(f"  Last: {last_time}")
                    # print(f"  Detected: {detection.detection_timestamp}")
                    # print(detection)
                    # exit(1)
            last_time = detection.detection_timestamp
        print(f"{station.name}: Detections in order")

        print()

    earliest_detection = min(
        [station.detections[0].detection_timestamp for station in stations]
    )
    print(
        f" * Race was at \t\t {datetime.utcfromtimestamp(earliest_detection).strftime('%Y-%m-%d %H:%M:%S')}"
    )

    # The start time of the mocking script
    start_time = time()
    pretty_start_time = datetime.utcfromtimestamp(start_time).strftime(
        "%Y-%m-%d %H:%M:%S"
    )
    print(f" * Mocking starting at \t {pretty_start_time}")

    # The difference in time of when we start the mocking script and from when we are replaying
    time_diff = start_time - mktime(START_MOCK_DATETIME.timetuple()) 
    pretty_time_diff = td_format(timedelta(seconds=time_diff))
    print(f" * Starting with a diff of {pretty_time_diff}")
    print()

    sleep(1)
    cursors = [0 for _ in range(len(stations))]
    glob_i = 0

    # Dump all detections from 'earliest_detection' until 'START_MOCK_DATETIME'
    print(f"Skipping detections until start time {START_MOCK_DATETIME}")
    for i, cursor in enumerate(cursors):
        while stations[i].detections[cursor].detection_timestamp < mktime(START_MOCK_DATETIME.timetuple()) :
            cursor+=1
        

        print(f"For station {stations[i].name}, skipped {cursor} detections at the start")
        cursors[i] = cursor
        

    did_process = False
    while True:
        now = time()
        duration_since_mock_start = (now - start_time) * MOCK_REPLAY_SPEED

        local_i = 0

        for i, cursor in enumerate(cursors):
            station = stations[i]
            if cursor >= len(stations[i].detections):
                continue

            did_process = True
            detection = station.detections[cursor]
            detection_time = detection.detection_timestamp
            while detection_time + time_diff < start_time + duration_since_mock_start:
                insert_detection(station, detection)
                # print(f"{glob_i}: {stations[i].detections[cursor]}")
                glob_i += 1
                local_i += 1
                cursor += 1

                detection = station.detections[cursor]
                detection_time = station.detections[cursor].detection_timestamp
            cursors[i] = cursor

        if did_process:
            did_process = False

            if local_i > 0:
                since_local_start = (now - start_time) * MOCK_REPLAY_SPEED
                pretty_time_diff = td_format(timedelta(seconds=since_local_start))
                print(f"{pretty_time_diff} in the race.\tSent {local_i} detections.")
            sleep(0.1)
        else:
            break


def main():
    start = timer()
    data_files = [f"data/ronny0{i}.dump.json" for i in range(1, 6)]
    data = []
    for station in config:
        with open(station.data_file(), "rb") as f:
            data_dict = orjson.loads(f.read())
            # use construct to skip validation, we have data from a trusted source
            data_obj = DataFile.construct(**data_dict)
            if data_obj.station_id != station.name:
                print(
                    "Datafile - Config mismatch. {station.data_file()} has id: {data_obj.station_id} but the config has {station.name}"
                )
                exit(1)

            station.detections = data_obj.detections
            data.append(station)

    end = timer()
    print("Took {:.2f} s to load all data".format(end - start))

    process(data)


if __name__ == "__main__":
    main()
