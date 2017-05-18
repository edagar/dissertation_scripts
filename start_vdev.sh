#! /bin/bash

sudo /local/dpdk_source/dpdk-17.02/build/app/testpmd -l 6-7 -n 4 -m 1024 \
    --vdev=virtio_user0,path=/usr/local/var/run/openvswitch/vhost0 \
    --file-prefix=container \
    -w "0000:04:00.1" \
    -- -i --txqflags=0xf00 --disable-hw-vlan --portmask=0x3
