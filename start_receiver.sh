#! /bin/bash

sudo rm /local/gitstuff/MoonGen/libmoon/dpdk-conf.lua
sudo cp dpdk-conf-recver.lua /local/gitstuff/MoonGen/libmoon/dpdk-conf.lua
#sudo ./run_moongen.sh "dump.lua 0" 
sudo ./run_moongen.sh "rx-pkts-distribution.lua 0" 
