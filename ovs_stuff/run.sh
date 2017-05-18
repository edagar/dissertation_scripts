#! /bin/bash

DB_SOCK=/usr/local/var/run/openvswitch/db.sock

# Stop existing OVS processes. kill -9 works too.
sudo /usr/local/share/openvswitch/scripts/ovs-ctl stop

#ovsdb-tool create /usr/local/etc/openvswitch/conf.db /usr/local/share/openvswitch/vswitch.ovsschema

sudo ovsdb-server \
    --remote=punix:$DB_SOCK \
    --remote=db:Open_vSwitch,Open_vSwitch,manager_options \
    --private-key=db:Open_vSwitch,SSL,private_key \
    --certificate=Open_vSwitch,SSL,certificate \
    --bootstrap-ca-cert=db:Open_vSwitch,SSL,ca_cert \
    --log-file=$OVS_LOG_DIR/ovsdb-server.log \
    --pidfile \
    --detach

sudo ovs-vsctl --no-wait set Open_vSwitch . \
     other_config:dpdk-init=true

     if test ! -e $1; then
       sudo ovs-vsctl --no-wait set Open_vSwitch . \
             other_config:dpdk-extra="$1 -n 4 --file-prefix=host"
     else
        sudo ovs-vsctl --no-wait set Open_vSwitch . \
         other_config:dpdk-extra="-l 0-6 --socket-mem=2048,0 -n 4 --file-prefix=host --master-lcore=6"

     fi

sudo ovs-vswitchd unix:$DB_SOCK \
    --pidfile \
    --detach
