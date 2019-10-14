#!/usr/bin/python
import os
import csv
import time
import json
import paramiko
from paramiko_expect import SSHClientInteraction
from datetime import datetime, date, timedelta, timezone

def dump(host, commands, date, save_dir):
    # 1: Cisco enable mode, 2: Linux prompt, you may need to add prompt expression
    PROMPT = ['.*>\s*', '.*#\s*', '.*$\s*']
    hostname, ipaddress, username, password = host[0], host[1], host[2], host[3]

    try:
        client = paramiko.SSHClient()
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        client.connect(hostname=ipaddress, username=username, password=password, timeout=10, look_for_keys=False)

        with SSHClientInteraction(client, timeout=30, display=False) as interact:
            interact.send('')
            index = interact.expect(PROMPT)

            for command in commands:
                if index == 0: # Alteon Platform compatible
                    interact.send(command)
                    output = interact.current_output_clean
                    filename = hostname + '_' + date + '.txt'
                    path = os.path.join(save_dir, filename)
                    with open(path, 'a') as config_file:
                        config_file.write(str(output) + '\n')

            interact.send('exit')
            index = interact.expect(PROMPT)

    except Exception as e:
        filename = hostname + '_' + date + '.txt'
        path = os.path.join(save_dir, filename)
        with open(path, 'a') as config_file:
            config_file.write(str(e) + '\n')

def main():
    today = datetime.today()
    date = "{0:%Y%m%d}".format(today)

    hosts = []
    commands = []
    commands.append('/c/d') # Configuration dump

    try:
        os.mkdir(str(date))
        with open('sample.csv', 'r') as host_file:
            reader = csv.reader(host_file)
            hosts = [host for host in reader]
    except Exception as e:
        print(e)

    cur_dir = os.getcwd()
    save_dir = cur_dir + '/' + date
    for host in hosts:
        dump(host, commands, date, save_dir)

if __name__ == '__main__':
    main()

