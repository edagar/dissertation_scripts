#! /bin/bash
    
sudo ovs-vsctl del-br br0
sudo ovs-vsctl set Open_vSwitch . other_config:pmd-cpu-mask=0x15

sudo ovs-vsctl add-br br0 -- set bridge br0 datapath_type=netdev

sudo ovs-vsctl add-port br0 dpdk0 -- set Interface dpdk0 type=dpdk options:dpdk-devargs=0000:06:00.0
sudo ovs-vsctl add-port br0 dpdk1 -- set Interface dpdk1 type=dpdk options:dpdk-devargs=0000:06:00.1

sudo ovs-vsctl set Interface dpdk0 options:n_rxq=2
sudo ovs-vsctl set Interface dpdk0 options:n_rxq_desc=128

sudo ovs-vsctl set interface dpdk0 other_config:pmd-rxq-affinity="0:2"

sudo ovs-ofctl add-flow br0 "in_port=1, actions=output:2"

sudo ovs-ofctl add-flow br0 "in_port=2, actions=output:1"
