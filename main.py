#!/usr/bin/python
import os
import csv
import time
import json
import paramiko
from datetime import datetime, date
from paramiko_expect import SSHClientInteraction

BACKUP_SERVER_FQDN = ''
BACKUP_SERVER_IP   = ''
BACKUP_USER = ''
BACKUP_PASS = ''
BACKUP_PATH = '/'
BACKUP_PORT = 22

def dump(host, commands, date, save_dir):
    # 1: Cisco enable mode, 2: Linux prompt, you may need to add prompt expression
    PROMPT = ['.*>\s*', '.*#\s*', '.*$\s*']
    print('Taking {} backup configuration file'.format(host[0]))
    hostname, ipaddress, username, password = host[0], host[1], host[2], host[3]

    try:
        client = paramiko.SSHClient()
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        client.connect(hostname=ipaddress, username=username, password=password, timeout=10, look_for_keys=False)

        with SSHClientInteraction(client, timeout=10, display=True) as interact:
            interact.send('')
            index = interact.expect(PROMPT)
            interact.expect('.*#\s')

            for command in commands:
                interact.send('')
                interact.expect('.*#\s')
                interact.send('n')
                interact.expect('.*#\s')
                output = interact.current_output_clean
                filename = hostname + '_' + date + '.txt'
                path = os.path.join(save_dir, filename)
                with open(path, 'a') as config_file:
                    config_file.write(str(output) + '\n')
            interact.send('exit')
            index = interact.expect(PROMPT)

    except Exception as e:
        print('Exception throws: {}'.format(e.args))

def backup(files, transport):
    try:
        for file in files:
            print('Transferring {} to the SFTP server'.format(file))
            sftp = paramiko.SFTPClient.from_transport(transport)
            sftp.put(file, BACKUP_PATH)
            sftp.close()
        except Exception as e:
            print('Exception throws with backup to the SFTP server: {}'.format(e.args))

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
            hosts = [host for host in reader if host != '']
            hosts.pop()
    except Exception as e:
        print('Exception throws: {}'.format(e.args))

    for host in hosts:
        ret = dump(host, commands, date, save_dir)
        if ret is not None:
            print('{} configuration backup has been taken successfully.'.format(ret))

    try:
        transport = paramiko.Transport((BACKUP_SERVER_IP, BACKUP_PORT))
        transport.connect(username=BACKUP_USER, password=BACKUP_PASS)
        backup(glob.glob(save_dir + '/*')), transport)
    except Exception as e:
        print('Exception throws with backup to the SFTP server:{}'.format(e.args))

if __name__ == '__main__':
    main()

