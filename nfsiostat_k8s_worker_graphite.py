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
DELAY = 30 #30 * 2 (Two iterations) = 60 seconds is the default delay, it can be changed by passing the command line arguments.

def get_iostat(delay):
    command = "nfsiostat {} 2".format(delay)
    #command = "iostat -x"
    process = subprocess.Popen(command, stdout=subprocess.PIPE, shell=True)
    stdout = process.communicate()[0].strip()
    lines = re.split('\n',stdout)
    total_lines = len(lines)+1
    total_mounts=total_lines/22

    nfsiostat_data=[]
    nfsiostat_data.append(['mount','R_ops_per_s','R_KB_per_s','R_KB_per_ops','R_avgRTT_ms','R_avgexe_ms','W_ops_per_s','W_KB_per_s','W_KB_per_ops','W_avgRTT_ms','W_avgexe_ms'])

    for x in range(total_mounts/2,total_mounts):
        l0 = str(lines[0+(x*22)].split()).strip('[]')

        l7 = str(lines[7+(x*22)].split()).strip('[]')
        l8 = str(lines[8+(x*22)].split()).strip('[]')
        l9 = str(lines[9+(x*22)].split()).strip('[]')
        l11 = str(lines[11+(x*22)].split()).strip('[]')
        l12 = str(lines[12+(x*22)].split()).strip('[]')

        l15 = str(lines[15+(x*22)].split()).strip('[]')
        l16 = str(lines[16+(x*22)].split()).strip('[]')
        l17 = str(lines[17+(x*22)].split()).strip('[]')
        l19 = str(lines[19+(x*22)].split()).strip('[]')
        l20 = str(lines[20+(x*22)].split()).strip('[]')

        nfsiostat_data.append([l0,l7,l8,l9,l11,l12,l15,l16,l17,l19,l20])

    substr1 = "pvc-"
    substr2 = "kubelet/pods/"
    substr3 = "/volumes/"
    for y in range(1,len(nfsiostat_data)):
        str1 = nfsiostat_data[y][0].strip('\"')
        if str1.find(substr1) != -1:
            rindx = str1.rindex(substr1)
            nfsiostat_data[y][0] = str1[rindx:-2]
        elif str1.find(substr2) != -1:
            rindx1 = str1.rindex(substr2)
            rindx2 = str1.rindex(substr3)
            nfsiostat_data[y][0] = str1[rindx1:rindx2]    
        str1 = nfsiostat_data[y][0]
        str1 = str1.replace('/', '-')
        str1 = str1.replace('.', '-')  
        nfsiostat_data[y][0] = str1
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
         
    delay = DELAY
    if len(sys.argv) > 1:
        arg = sys.argv[1]
        if arg.isdigit():
            delay = int(arg)
        else:
            sys.stderr.write("Ignoring non-integer argument. Using default: %ss\n" % delay)         

    command1 = "ifconfig eth0 | grep 'inet addr:' | cut -d: -f2 | awk '{ print $1}'"
    process1 = subprocess.Popen(command1, stdout=subprocess.PIPE, shell=True)
    stdout1 = process1.communicate()[0].strip()
    hostname=stdout1.replace('.', '-')

    sock = socket.socket()
    try:
        sock.connect( (CARBON_SERVER, CARBON_PICKLE_PORT) )
    except socket.error:
        raise SystemExit("Couldn't connect to %(server)s on port %(port)d, is carbon-cache.py running?" % { 'server':CARBON_SERVER, 'port':CARBON_PICKLE_PORT })

    run(sock, delay, hostname)

if __name__ == "__main__":
    main()
