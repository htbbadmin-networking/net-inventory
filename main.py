#!/usr/bin/python3

#highlight new hosts
#highlight missing hosts
#highlight new ports
#highlight missing ports
#search by date range
#format strings bad

import nmap
import sqlite3
import datetime
import argparse

def open(database):
    conn = sqlite3.connect(database)
    c = conn.cursor()
    return conn

def check_tables(conn, check_table):
    exists = False
    c = conn.cursor()
    tables = c.execute("SELECT NAME FROM sqlite_master WHERE TYPE = 'table';").fetchall()
    for table in tables:
        if check_table in table:
            exists = True
    return exists

def create_table(conn, table_name, fields):
    c = conn.cursor()
    new_table_start = "CREATE TABLE "
    new_table_end = ""
    query = new_table_start + table_name + " " + fields + new_table_end
    print(query)
    c.execute(query)
    conn.commit
    return

def scan_ip_range(range):
    nm = nmap.PortScanner()
    pingable_hosts = nm.scan(range, arguments='-sn')
    print("nmap discovered hosts")
    return pingable_hosts['scan']

def insert_host(conn, host):
    c = conn.cursor()
    insert = "INSERT INTO hosts VALUES ('{}', '{}', '{}', DATETIME('now'));".format(host, '', datetime.datetime.now(), datetime.datetime.now())
    c.execute(insert)
    conn.commit()
    return

def test_read(conn):
    c = conn.cursor()
    db_hosts = c.execute('SELECT ip FROM hosts')
    conn.commit()
    return db_hosts.fetchall()

def close(conn):
    conn.close()

def main():
    range = '192.168.0.0-254'
    database = 'inventory.db'

    conn = open(database)

    if not check_tables(conn, 'hosts'):
        print("Creating table")
        create_table(conn, 'hosts', "('ip', 'hostname', 'first_seen', 'last_seen')")

    pingable_hosts = scan_ip_range(range)
    print("pingable hosts")
    for host in pingable_hosts:
        print(host)

    db_hosts = test_read(conn)
    print("DB Hosts Before Insert: ")
    for host in db_hosts:
        print(host)

    for pingable_host in pingable_hosts:
        new = True
        for db_host in db_hosts:
            db_host = ' '.join(map(str, db_host))
            if pingable_host in db_host:
                new = False
        if new:
            insert_host(conn, pingable_host)

    print("DB Hosts After Insert: ")
    host_list = test_read(conn)
    for host in host_list:
        print(' '.join(map(str, host)))

    close(conn)

if __name__ == '__main__':
    main()
