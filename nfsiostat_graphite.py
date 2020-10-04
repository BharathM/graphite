#!/usr/bin/python

import re
import sys
import time
import socket
import platform
import subprocess
import pickle
import struct

CARBON_SERVER = '10.96.152.46'
CARBON_PICKLE_PORT = 2004
DELAY = 30  #30 * 2 (Two iterations) = 60 seconds is the default delay, it can be changed by passing the command line arguments.
MACHINE_NAME = 'h'  # h - Metric based on the POD/VM hostname, ip - Metric based on the IP address of POD or VM

def get_iostat(delay):
    command = "nfsiostat {} 2".format(delay)
    process = subprocess.Popen(command, stdout=subprocess.PIPE, shell=True)
    stdout = process.communicate()[0].strip()
    lines = re.split('\n',stdout)
    total_lines = len(lines)+1
    total_mounts=total_lines/9

    nfsiostat_data=[]
    nfsiostat_data.append(['mount','R_ops_per_s','R_KB_per_s','R_KB_per_ops','R_avgRTT_ms','R_avgexe_ms','W_ops_per_s','W_KB_per_s','W_KB_per_ops','W_avgRTT_ms','W_avgexe_ms'])

    for x in range(total_mounts/2,total_mounts):
        temp1 = lines[0 + (x * 9)]
        if temp1.find('/pmnt/') != -1:
            rindx = temp1.rindex('/pmnt/')
            temp1 = temp1[rindx+6:-1]
        temp1 = temp1.replace('.', '-')
        temp1 = temp1.replace(' ', '_')
        temp1 = temp1.replace('/', '_')
        l0 = temp1

        temp1 = lines[5 + (x * 9)]
        temp1 = temp1.split()
        l1 = temp1[0]
        l2 = temp1[1]
        l3 = temp1[2]
        l4 = temp1[5]
        l5 = temp1[6]

        temp1 = lines[7 + (x * 9)]
        temp1 = temp1.split()
        l6 = temp1[0]
        l7 = temp1[1]
        l8 = temp1[2]
        l9 = temp1[5]
        l10 = temp1[6]

        nfsiostat_data.append([l0,l1,l2,l3,l4,l5,l6,l7,l8,l9,l10])

    return nfsiostat_data

def run(sock, delay, hostname):
    while True:
        tuples = ([])
        lines = []
        iostat_data = get_iostat(delay)
        now = int(time.time())
        r=len(iostat_data)
        c=len(iostat_data[0])
        for x in range(1,r):
            for y in range(1,c):
                tuples.append((hostname+'.nfsiostat.'+iostat_data[x][0].strip('\"')+'.'+iostat_data[0][y].strip('\"'), (now,iostat_data[x][y].strip('\"\''))))
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
        sock.connect( (CARBON_SERVER, CARBON_PICKLE_PORT) )
    except socket.error:
        raise SystemExit("Couldn't connect to %(server)s on port %(port)d, is carbon-cache.py running?" % { 'server':CARBON_SERVER, 'port':CARBON_PICKLE_PORT })

    run(sock, delay, hostname)


if __name__ == "__main__":
    main()
