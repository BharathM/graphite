#!/usr/bin/python
#

import re
import sys
import time
import socket
import subprocess
import pickle
import struct

CARBON_SERVER = '10.96.152.46'
CARBON_PICKLE_PORT = 2004
DELAY = 60  # 60 seconds is the default delay, it can be changed by passing the command line arguments.
MACHINE_NAME = 'h'  # h - Metric based on the POD/VM hostname, ip - Metric based on the IP address of POD or VM


def get_iostat(delay):
    command = "iostat -xdy {} 1".format(delay)
    process = subprocess.Popen(command, stdout=subprocess.PIPE, shell=True)
    stdout = process.communicate()[0].strip()
    # Error logic to check iostat exists and data showing
    postString = stdout.split("\n", 2)[2]
    lines = re.split('\n', postString)
    iostat_data = []
    for line in lines:
        iostat_data.append(line.split())
    iostat_data[0] = [w.replace('/', '_per_') for w in iostat_data[0]]
    iostat_data[0] = [w.replace('%', 'percent_') for w in iostat_data[0]]
    return iostat_data


def run(sock, delay, hostname):
    while True:
        tuples = ([])
        lines = []
        iostat_data = get_iostat(delay)
        now = int(time.time())
        r = len(iostat_data)
        c = len(iostat_data[0])
        for x in range(1, r):
            for y in range(1, c):
                tuples.append(
                    (hostname + '.iostat.' + iostat_data[x][0] + '.' + iostat_data[0][y], (now, iostat_data[x][y])))
        package = pickle.dumps(tuples, 1)
        size = struct.pack('!L', len(package))
        sock.sendall(size)
        sock.sendall(package)


def main():
    delay = DELAY
    input2 = MACHINE_NAME

    if len(sys.argv) > 1:
        arg = sys.argv[1]
        if arg.isdigit():
            delay = int(arg)
        else:
            sys.stderr.write("Ignoring 1st non-integer argument. Using default: %ss\n" % delay)
        arg1 = sys.argv[2]
        if arg1=="ip" or arg1=="h":
            input2 = str(arg1)
        else:
            input2 = MACHINE_NAME
            sys.stderr.write("Ignoring 2nd argument. Using default: %ss\n" % input2)

    if input2=="ip":
        # This command fail if the eth0 dosen't exist, need to add a logic to overcome this issue
        command1 = "ifconfig eth0 | grep 'inet addr:' | cut -d: -f2 | awk '{ print $1}'"
        process1 = subprocess.Popen(command1, stdout=subprocess.PIPE, shell=True)
        stdout1 = process1.communicate()[0].strip()
        hostname = stdout1.replace('.', '-')
    else:
        command1 = "hostname"
        process1 = subprocess.Popen(command1, stdout=subprocess.PIPE, shell=True)
        stdout1 = process1.communicate()[0].strip()
        hostname = stdout1.replace('.', '-')

    sock = socket.socket()
    try:
        sock.connect((CARBON_SERVER, CARBON_PICKLE_PORT))
    except socket.error:
        raise SystemExit(
            "Couldn't connect to %(server)s on port %(port)d, is carbon-cache.py running?" % {'server': CARBON_SERVER,
                                                                                              'port': CARBON_PICKLE_PORT})

    run(sock, delay, hostname)


if __name__ == "__main__":
    main()
