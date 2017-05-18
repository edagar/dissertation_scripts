#! /bin/bash

sudo docker exec $1 cat /ovs/log/ovs-vswitchd.log
