#! /bin/bash

#sudo ./l2fwd -c 0x3 -n 4 --socket-mem=2048,0 --file-prefix=l2fwd $1 -- -q 1 -p 0x3
#sudo ./l2fwd -l 0-6 -n 4 --socket-mem=2048,0 --file-prefix=l2fwd $1 -- -q 2 -p 0x3
#sudo taskset 0x1  ./l2fwd -c 0x1 -n 4 --socket-mem=2048,0 --file-prefix=l2fwd $1 -- -q 2 -p 0x3 --rxd=1

#sudo ./start_single_container.py -i $1 -o $2 -p 0x1 --n_rxq=1

#sudo taskset 0x15 ./testpmd -c 0x15 -n 4 --master-lcore=4 --socket-mem=2048,1024 --file-prefix=l2fwd -- -a --portmask=0x3 --nb-cores=2 --numa --socket-num=0 --rxq=1

sudo taskset 0x5 ./testpmd -l 0,2 -n 4 --master-lcore=0 --socket-mem=2048,1024 --file-prefix=l2fwd -- -a --portmask=0x3 --nb-cores=1 --numa --socket-num=0 --rxq=1
