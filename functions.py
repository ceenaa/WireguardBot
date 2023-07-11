import subprocess
import datetime

import pytz as pytz
from dotenv.main import load_dotenv
import os

import db
import models

load_dotenv()
conf_name = os.environ.get("CONF_NAME")
sys_name = os.environ.get("SYSTEM_NAME")

peerMap = {}
sortedPeer = []
total = 0


def extract_data():
    file = open("wg.txt", "w")
    wg = subprocess.check_output(f"wg show {sys_name} dump", shell=True)
    file.write(wg.decode("utf-8"))
    file.close()
    file = open("wg.txt", "r")
    lines = file.readlines()
    file.close()
    return lines


def convert_byte_to_gib(byte):
    gb = byte / 1024 / 1024 / 1024
    gb = format(gb, '.2f')
    return float(gb)


def reload():
    global total, sortedPeer, peerMap
    lines = extract_data()
    lines = lines[1:]
    connection = db.connect()
    total = db.get_usage_for_name(connection, conf_name)[2]
    tehran_timezone = pytz.timezone('Asia/Tehran')

    for line in lines:
        line = line.split("\t")
        public_key = line[0]
        pre_shared_key = line[1]
        endpoint = line[2]
        allowed_ips = line[3]
        timestamp = int(line[4])
        dt = datetime.datetime.fromtimestamp(timestamp)
        tehran_dt = dt.astimezone(tehran_timezone)
        formatted_datetime = tehran_dt.strftime("%Y-%m-%d %H:%M:%S")
        latest_handshake = formatted_datetime

        transfer = float(db.get_transfer(connection, public_key)[0])
        transfer += float(line[5]) + float(line[6])
        total += transfer
        transfer = convert_byte_to_gib(transfer)
        name = db.get_user_name(connection, public_key)
        p = models.Peer(name, public_key, pre_shared_key, endpoint, allowed_ips, latest_handshake, transfer, 1)
        peerMap[name] = p

    total = format(total, '.2f')
    total = float(total)
    sortedPeer = sorted(peerMap.values(), key=lambda x: x.transfer, reverse=True)
    connection.close()


def pause_user(name):
    reload()
    connection = db.connect()
    db.update_user(connection, peerMap[name])
    db.deactivate_user(connection, name)
    connection.commit()
    connection.close()
    db.add_total_usage_by_name(connection, name, peerMap[name].transfer)
    command = f"wg set {sys_name} peer \"{peerMap[name].public_key}\" remove"
    os.system(command)
    command = f"ip -4 route delete {peerMap[name].allowed_ips} dev {conf_name}"
    os.system(command)


def resume_user(name):
    connection = db.connect()
    db.activate_user(connection, name)
    connection.commit()
    arr = db.get_user(connection, name)
    p = models.Peer(arr[0], arr[1], arr[2], arr[3], arr[4], arr[5], arr[6], arr[7])
    command = f"wg set {sys_name} peer \"{p.public_key}\" allowed-ips {p.allowed_ips}" \
              f" preshared-key <(echo {p.pre_shared_key})"
    os.system(command)
    command = f"ip -4 route add {p.allowed_ips} dev {conf_name}"
    os.system(command)
    connection.close()


def export():
    reload()
    file = open("data.txt", "w")
    for peer in sortedPeer:
        file.write(str(peer) + "\n")
    file.close()
