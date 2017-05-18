#! /bin/bash

sudo rm /local/gitstuff/MoonGen/libmoon/dpdk-conf.lua
sudo cp dpdk-conf-default.lua /local/gitstuff/MoonGen/libmoon/dpdk-conf.lua
sudo ./run_moongen.sh "packet-sizes-rx.lua 0 1"
