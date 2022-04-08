from timeit import default_timer as timer
from time import sleep, time

from datetime import datetime, timedelta
from typing import List, Optional
import json

import dataclasses, orjson, typing, psycopg2

from helpers.formatters import td_format
from schemas import DataFile, Detection

from config import config

import requests
import os

telraam_url: str = os.getenv("TELRAAM_URL", "http://127.0.0.1:8080")
DEBUG_REQUESTS = False

if DEBUG_REQUESTS:
    import logging
    from http.client import HTTPConnection  # py3

    log = logging.getLogger("urllib3")
    log.setLevel(logging.DEBUG)

    # logging from urllib3 to console
    ch = logging.StreamHandler()
    ch.setLevel(logging.DEBUG)
    log.addHandler(ch)

    # print statements from `http.client.HTTPConnection` to console/stdout
    HTTPConnection.debuglevel = 1


def list_datadump_batons():
    start = timer()
    data_files = [f"data/ronny0{i}.dump.json" for i in range(1, 6)]
    data = []
    batons = set()
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

            for detection in data_obj.detections:
                batons.add(detection.mac)

    end = timer()

    print()
    print("Took {:.2f} s to load all data".format(end - start))
    print("Batons found in data dump")
    print("-------------------------")
    for baton in sorted(list(batons)):
        print(baton)

    return batons


def list_telraam_batons():
    print()
    print("Current configured batons in telraam")
    print("------------------------------------")
    resp = requests.get(f"{telraam_url}/baton")
    batons = resp.json()
    for baton in batons:
        print(f"Baton: {baton}")

    return resp.json()


def sync_batons(telraam_batons, datadump_batons):
    telraam_baton_mac_set = {baton["mac"] for baton in telraam_batons}

    batons_only_in_telraam = telraam_baton_mac_set.difference(datadump_batons)
    batons_already_present = telraam_baton_mac_set.intersection(datadump_batons)
    batons_missing = datadump_batons.difference(telraam_baton_mac_set)
    print()
    print("Batons already present in telraam")
    for baton in sorted(list(batons_already_present)):
        print(baton)
    print()
    print("Batons missing in telraam")
    for baton in sorted(list(batons_missing)):
        print(baton)
    print()

    if len(batons_missing) > 0:
        answer = input("Create missing batons? (Y/n)")
        if answer in ["", "Y", "y"]:
            print("Batons will be named 'Baton <letter>'")
            print("<letter> will be incremented for every baton")
            start_letter = input("Enter letter to start at: ")

            start_letter_num = ord(start_letter)
            for i, baton in enumerate(sorted(list(batons_missing))):
                name = f"Baton {chr(start_letter_num + i)}"
                print(f"Creating baton : [mac -> {baton}, name -> {name}]")
                resp = requests.post(
                    f"{telraam_url}/baton",
                    json={"mac": baton, "name": name},
                    headers={
                        "accept": "application/json",
                        "Content-Type": "application/json",
                    },
                )
                print(f"response code: {resp.status_code}")
        else:
            print("Not syncing..")

    print()
    print("Batons present in telraam but not in our dump")
    for baton in batons_only_in_telraam:
        print(baton)


def setup_batons():
    telraam_batons = list_telraam_batons()
    datadump_batons = list_datadump_batons()

    sync_batons(telraam_batons, datadump_batons)


if __name__ == "__main__":
    setup_batons()
