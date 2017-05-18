#! /bin/bash

sudo rm /local/gitstuff/MoonGen/libmoon/dpdk-conf.lua
sudo cp dpdk-conf-default.lua /local/gitstuff/MoonGen/libmoon/dpdk-conf.lua
sudo ./run_moongen.sh "l3-load-latency.lua -s $1 0 1"
#sudo ./run_moongen.sh "latency-packet-sizes.lua 0 1"
