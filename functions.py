import subprocess
import datetime as date

import pytz as pytz
from dotenv.main import load_dotenv
import os

import db
import models
import sheet

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


def total_days():
    connection = db.connect()
    _, start_time, _ = db.get_usage_for_name(connection, conf_name)
    connection.close()
    start_time = start_time.split("-")
    start_time = date.date(year=int(start_time[0]), month=int(start_time[1]), day=int(start_time[2]))

    now_time = date.date.today()
    return (now_time - start_time).days


def data_base_to_peer_map():
    global peerMap
    connection = db.connect()
    peers = db.get_all_users(connection)
    connection.close()
    for peer in peers:
        p = models.Peer(peer[0], peer[1], peer[2], peer[3], peer[4], peer[5], peer[6], peer[7])
        peerMap[peer[0]] = p


def reload():
    global total, sortedPeer, peerMap
    lines = extract_data()
    lines = lines[1:]
    connection = db.connect()
    total = db.get_usage_for_name(connection, conf_name)[2]
    tehran_timezone = pytz.timezone('Asia/Tehran')
    data_base_to_peer_map()

    for line in lines:
        line = line.split("\t")
        public_key = line[0]
        pre_shared_key = line[1]
        endpoint = line[2]
        allowed_ips = line[3]
        timestamp = int(line[4])
        dt = date.datetime.fromtimestamp(timestamp)
        tehran_dt = dt.astimezone(tehran_timezone)
        formatted_datetime = tehran_dt.strftime("%Y-%m-%d %H:%M:%S")
        latest_handshake = formatted_datetime

        transfer = float(db.get_transfer(connection, public_key)[0])
        transfer += convert_byte_to_gib(float(line[5]) + float(line[6]))
        total += convert_byte_to_gib(float(line[5]) + float(line[6]))
        transfer = format(transfer, '.2f')
        transfer = float(transfer)
        name = db.get_user_name(connection, public_key)
        p = models.Peer(name, public_key, pre_shared_key, endpoint, allowed_ips, latest_handshake, transfer, 1)
        peerMap[name] = p

    total = format(total, '.2f')
    total = float(total)
    sortedPeer = sorted(peerMap.values(), key=lambda x: x.transfer, reverse=True)
    connection.close()
    sheet.main()


def pause_user(name):
    if peerMap[name].active == 0:
        raise Exception("User is already paused")
    reload()
    connection = db.connect()
    db.update_user(connection, peerMap[name])
    connection.commit()
    db.deactivate_user(connection, name)
    connection.commit()
    db.add_total_usage_by_name(connection, name, peerMap[name].transfer)
    connection.commit()
    command = f"wg set {sys_name} peer \"{peerMap[name].public_key}\" remove"
    os.system(command)
    command = f"ip -4 route delete {peerMap[name].allowed_ips} dev {sys_name}"
    os.system(command)

    connection.close()
    reload()


def resume_user(name):
    if peerMap[name].active == 1:
        raise Exception("User is already active")
    connection = db.connect()
    db.activate_user(connection, name)
    connection.commit()
    db.set_transfer_to_zero(connection, name)
    connection.commit()
    arr = db.get_user(connection, name)
    p = models.Peer(arr[0], arr[1], arr[2], arr[3], arr[4], arr[5], arr[6], arr[7])
    command1 = f"wg set {sys_name} peer \"{p.public_key}\" allowed-ips {p.allowed_ips} " \
               f"preshared-key <(echo \"{p.pre_shared_key}\")"
    command2 = f"ip -4 route add {p.allowed_ips} dev {sys_name}"
    subprocess.run(['bash', '-c', command1])
    subprocess.run(['bash', '-c', command2])

    connection.close()
    reload()


def export():
    reload()
    file = open("data.txt", "w")
    for peer in sortedPeer:
        file.write(str(peer) + "\n")
    file.close()
