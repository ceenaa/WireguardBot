import datetime
import sqlite3

import functions


def connect():
    return sqlite3.connect("db.sqlite3")


def create_table(conn):
    c = conn.cursor()
    c.execute("""CREATE TABLE users (
                name text,
                public_key text primary key not null unique,
                pre_shared_key text,
                endpoint text,
                allowed_ips text,
                latest_handshake text,
                transfer real,
                active boolean
                )""")

    c.execute("""CREATE TABLE usages (
        name text,
        date text,
        transfer real
        )
    """)


def get_all_users(conn):
    c = conn.cursor()
    c.execute("SELECT * FROM users")
    return c.fetchall()


def get_all_usages(conn):
    c = conn.cursor()
    c.execute("SELECT * FROM usages")
    return c.fetchall()


def get_user_name(conn, public_key):
    c = conn.cursor()
    c.execute("SELECT name FROM users WHERE public_key = ?", (public_key,))
    return c.fetchone()[0]


def get_transfer(conn, public_key):
    c = conn.cursor()
    c.execute("SELECT transfer FROM users WHERE public_key = ?", (public_key,))
    return c.fetchone()


def get_user(conn, name):
    c = conn.cursor()
    c.execute("SELECT * FROM users WHERE name = ?", (name,))
    return c.fetchone()


def paused_users(conn):
    c = conn.cursor()
    c.execute("SELECT * FROM users WHERE active = 0")
    return c.fetchall()


def update_user(conn, peer):
    c = conn.cursor()
    c.execute("INSERT OR REPLACE INTO users VALUES(?, ?, ?, ?, ?, ?, ?, ?)",
              (peer.name, peer.public_key, peer.pre_shared_key, peer.endpoint, peer.allowed_ips,
               peer.latest_handshake, peer.transfer, peer.active))


def deactivate_user(conn, public_key):
    c = conn.cursor()
    c.execute("UPDATE users SET active = 0 WHERE public_key = ?", (public_key,))


def set_transfer_to_zero(conn, name):
    c = conn.cursor()
    c.execute("UPDATE users SET transfer = 0 WHERE name = ?", (name,))


def activate_user(conn, public_key):
    c = conn.cursor()
    c.execute("UPDATE users SET active = 1 WHERE public_key = ?", (public_key,))


def make_usage_for_name(conn, name):
    c = conn.cursor()
    c.execute("INSERT OR REPLACE INTO usages VALUES(?, ?, ?)", (name, "2023-07-11", 0))


def get_usage_for_name(conn, name):
    c = conn.cursor()
    c.execute("SELECT * FROM usages WHERE name = ?", (name,))
    return c.fetchone()


def add_total_usage_by_name(conn, name, transfer):
    c = conn.cursor()
    c.execute("UPDATE usages SET transfer = transfer + ? WHERE name = ?", (transfer, name))


def initialize_users(conn):
    c = conn.cursor()
    file = open("/etc/wireguard/" + functions.sys_name + ".conf", "r")
    # file = open("peers.txt", "r")
    lines = file.readlines()
    file.close()
    for i in range(13, len(lines), 6):
        name = lines[i]
        name = name.split(" ")[1]
        public_key = lines[i + 2]
        public_key = public_key.split(" = ")[1]
        public_key = public_key.strip()
        pre_shared_key = lines[i + 4]
        pre_shared_key = pre_shared_key.split(" = ")[1]
        pre_shared_key = pre_shared_key.strip()
        allowed_ips = lines[i + 3]
        allowed_ips = allowed_ips.split(" = ")[1]
        allowed_ips = allowed_ips.strip()
        transfer = 0
        last_handshake = "None"
        endpoint = "None"
        active = True
        if lines[i + 1][0] == "#":
            active = False

        c.execute("INSERT OR REPLACE INTO users VALUES(? ,? ,? ,?, ?, ?, ?, ?)",
                  (name, public_key, pre_shared_key, endpoint, allowed_ips, last_handshake, transfer, active))


def import_data(conn):
    c = conn.cursor
    file = open("data.txt", "r")
    lines = file.readlines()
    file.close()
    for line in lines:
        line = line.split("\t")
        name = line[0]
        public_key = line[1]
        pre_shared_key = line[2]
        endpoint = line[3]
        allowed_ips = line[4]
        latest_handshake = line[5]
        transfer = line[6]
        active = line[7].strip()
        c.execute("INSERT OR REPLACE INTO users VALUES(?, ?, ?, ?, ?, ?, ?, ?)",
                  (name, public_key, pre_shared_key, endpoint, allowed_ips,
                   latest_handshake, transfer, active))
