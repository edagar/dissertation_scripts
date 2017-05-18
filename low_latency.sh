#! /bin/bash

sudo ./start_single_container.py -i $1 -o $2 -c 0-6 --master_core=6 -p 0x15 --n_rxq=2
