# iostat_graphite.py
Capture the iostat output and send it to the Graphite server using Python Pickele server. The default time delay was set to 60 seconds, this can be changed by sending the command line parameters. Program can handle any number of devices in the iostat output. This program should work on any distribution of the linux.

# nfsiostat_graphite.py
Capture the nfsiostat output and send it to the Graphite server using Python Pickele server. The default time delay was set to 60 seconds, this can be changed by sending the command line parameters. This program should work on any distribution of the linux. This program was designed to handle the garbled output as shown below, need to make few changes based on your nfsiostat output.

xxxxxxxxx:/ifs/data/cust01/nfs/k8s-isnfs/xxxxxxxx-customscript-pvc-pvc-29cc294e-83ef-42bd-b565-0e1edcc256ee/xxxxxxxxx-customscript mounted on /var/vcap/data/kubelet/pods/eb7e27e2-6ace-4297-ab39-df43f64a250f/volume-subpaths/pvc-29cc294e-83ef-42bd-b565-0e1edcc256ee/perf23250-d2customscript/0:

   op/s         rpc bklog
   6.72
           0.00
read:
  ops/s            kB/s           kB/op         retrans         avg RTT (ms)    avg exe (ms)
                  0.000
          0.000
          2.822
       0 (0.0%)
          0.909
          0.909
write:
  ops/s            kB/s           kB/op         retrans         avg RTT (ms)    avg exe (ms)
                  0.025
         14.823
        587.597
       0 (0.0%)
         13.444
        478.395

These programs are used used identify the disk bottlenecks and capture the I/O throughput.

# Prerequiste
1. Linux vm.
2. Python 2.X (I have not tried on Python 3.X, it should work, I initially had issues with the outout format so started using the Python 2.X.
3. Sysstat package
3. nfs-utils package
4. Graphite server https://graphiteapp.org/

# How to run the program?
python iostat_graphite.py
python nfsiostat_graphite.py

# How to run the program in background, make sure it dosen't get stopped and log any errors if there any?
nohup python nfsiostat_graphite.py < /dev/null > nfsiostat_graphite.log 2>&1 &
