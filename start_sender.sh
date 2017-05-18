#! /bin/bash

sudo rm /local/gitstuff/MoonGen/libmoon/dpdk-conf.lua
sudo cp dpdk-conf-sender.lua /local/gitstuff/MoonGen/libmoon/dpdk-conf.lua
#sudo ./run_moongen.sh "l3-load-latency.lua 0 0"
sudo ./run_moongen.sh "udp-throughput.lua 0"
