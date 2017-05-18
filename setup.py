#! /usr/bin/python2

from os import popen as _popen
import sys
from time import sleep

def popen(a, b="r"):
    print("%s\n" % a)
    return _popen(a, b)

DPDK_SCRIPT_DIR = "/local/gitstuff/MoonGen/libmoon/deps/dpdk/tools"
DPDK_KMOD_DIR   = "/local/gitstuff/MoonGen/libmoon/deps/dpdk/x86_64-native-linuxapp-gcc/kmod"
DEVBIND_SCRIPT  = "%s/dpdk-devbind.py" % DPDK_SCRIPT_DIR
CONTAINER_NAME  = "ovs"
IMAGE_NAME      = "edagar/ovs-dpdk2"
IMAGE_NAME_MID  = "socketplane/openvswitch"
#IMAGE_NAME_MID  = "edagar/ovs-dpdk"
HUGEPAGE_SCRIPT = "setup-hugetlbfs.sh"
INTERFACE_FILE  = "bound_interfaces"
CONTAINERS_FILE = "started_containers"


DEFAULT_DPDK_MEM_ENTRY      = "1024,0"
DEFAULT_DPDK_CORES_ENTRY    = "0-4"
DEFAULT_DPDK_PMD_MASK_ENTRY = "0f"

DEFAULT_DPDK_MEM_EXIT      = "0,1024"
DEFAULT_DPDK_CORES_EXIT    = "10-20"
DEFAULT_DPDK_PMD_MASK_EXIT = "f000"

settings = {
        "num_containers" : None,
        "entry_iface"    : None,
        "exit_iface"     : None,
        "phoronix"       : False
    }

def usage():
    print("Usage: %s ..." % sys.argv[0])
    exit(1)

def parse_args(args):
    if len(args) == 1 and args[0] == "--reset":
        reset()
        exit(0)

    if len(args) < 2:
        usage()

    for index, flag in enumerate(args):
        if flag == "-n":
            settings['num_containers'] = int(args[index + 1])

        elif flag == "--entry":
           settings['entry_iface'] = args[index + 1] 

        elif flag == "--exit":
           settings['exit_iface'] = args[index + 1] 

        elif flag == "--phoronix":
            settings['phoronix'] = True

def run_phoronix():
    pass

def setup_entry_container(name, veth_index, container_pids, index, entry):
    #create a pair of veth interfaces
    """popen("sudo ip link add veth%d type veth peer name veth%d" % (veth_index, veth_index + 1), "r")

    #assign one veth endpoint to the ns of the first container and set it to up
    popen("sudo ip link set veth%d netns ns-%d" % (veth_index, container_pids[index]), "r")
    popen("sudo ip netns exec ns-%d ip link set dev veth%d up" % (container_pids[index], veth_index), "r")

    #assign the other veth endpoint to the ns of the second container and set it to up
    popen("sudo ip link set veth%d netns ns-%d" % (veth_index+1, container_pids[index+1]), "r")
    popen("sudo ip netns exec ns-%d ip link set dev veth%d up" % (container_pids[index+1], veth_index+1), "r")"""

    #setup ovs-dpdk in entry container
    popen("docker exec %s ovs-vsctl del-br br0" % name, "r")

    popen("docker exec %s rm -f /usr/local/var/run/openvswitch/sockets/vhost-user-1" % name)

    popen("sudo docker exec %s ovs-vsctl set Open_vSwitch . other_config:pmd-cpu-mask=%s" % (name, "0x5"))

    popen("docker exec %s ovs-vsctl add-br br0 -- set bridge br0 datapath_type=netdev" % name, "r")

    popen("docker exec %s ovs-vsctl add-port br0 dpdk0 -- set Interface dpdk0 type=dpdk options:dpdk-devargs=%s" % (name, str(entry[1])), "r")

    popen('docker exec %s ovs-vsctl add-port br0 vhost-user-1 -- set Interface vhost-user-1 type=dpdkvhostuser' % (name), "r")
    #popen("docker exec %s ovs-vsctl add-port br0 veth%d" % (name, veth_index), "r")

    popen("docker exec %s ovs-vsctl set Interface dpdk0 options:flow-ctrl-autoneg=false" % name)
    popen("docker exec %s ovs-vsctl set Interface dpdk0 options:tx-flow-ctrl=false" % name)
    popen("docker exec %s ovs-vsctl set Interface dpdk0 options:rx-flow-ctrl=false" % name)



    popen('docker exec %s ovs-ofctl add-flow br0 "in_port=1, actions=output:2"' % (name), "r")
    popen('docker exec %s ovs-ofctl add-flow br0 "in_port=2, actions=output:1"' % (name), "r")

def setup_exit_container(name, veth_index, container_pids, index, exit):
    #set ovs-dpdk in exit container
    popen("docker exec %s ovs-vsctl del-br br0" % name, "r")
    popen("sudo docker exec %s ovs-vsctl set Open_vSwitch . other_config:pmd-cpu-mask=%s" % (name, "0x500"))

    popen("docker exec %s ovs-vsctl add-br br0 -- set bridge br0 datapath_type=netdev" % name, "r")

    #popen("docker exec %s ovs-vsctl add-port br0 veth%d" % (name, veth_index), "r")

    popen('docker exec container1 ovs-vsctl add-port br0 vhost-client-1 -- set Interface vhost-client-1 type=dpdkvhostuserclient options:vhost-server-path=/usr/local/var/run/openvswitch/sockets/vhost-user-1')

    popen("docker exec %s ovs-vsctl add-port br0 dpdk0 -- set Interface dpdk0 type=dpdk options:dpdk-devargs=%s" % (name, str(exit[1])), "r")

    popen("docker exec %s ovs-vsctl set Interface dpdk0 options:flow-ctrl-autoneg=false" % name)
    popen("docker exec %s ovs-vsctl set Interface dpdk0 options:tx-flow-ctrl=false" % name)
    popen("docker exec %s ovs-vsctl set Interface dpdk0 options:rx-flow-ctrl=false" % name)

    popen('docker exec %s ovs-ofctl add-flow br0 "in_port=1, actions=output:2"' % (name), "r")
    popen('docker exec %s ovs-ofctl add-flow br0 "in_port=2, actions=output:1"' % (name), "r")

def setup_middle_container(name, veth_index, container_pids, index):
    def setup_container_ovs(cmds, name, n):
        map(lambda cmd: popen("sudo docker exec %s %s" % 
            (name, 
            cmd.replace("<n>", str(n)).replace("<n+2>", str(n+2)).replace("<n+1>", str(n+1))),
            "r"), cmds)

    middle_container_cmds = [
        #"ovs-vsctl add-br br<n> -- set bridge br<n> datapath_type=netdev",
        "ovs-vsctl add-br br<n>",
        "ovs-vsctl add-port br<n> veth<n>",
        "ovs-vsctl add-port br<n> veth<n+1>",
        'ovs-ofctl add-flow br<n> "in_port=1, actions=output:2"',
        'ovs-ofctl add-flow br<n> "in_port=2, actions=output:1"'
    ]

    #create a pair of veth interfaces
    popen("sudo ip link add veth%d type veth peer name veth%d" % (veth_index, veth_index + 1), "r")

    #assign one veth endpoint to the ns of the current container and set it to up
    popen("sudo ip link set veth%d netns ns-%d" % (veth_index, container_pids[index]), "r")
    popen("sudo ip netns exec ns-%d ip link set dev veth%d up" % (container_pids[index], veth_index), "r")

    #assign the other veth endpoint to the ns of the next container and set it to up
    popen("sudo ip link set veth%d netns ns-%d" % (veth_index + 1, container_pids[index+1]), "r")
    popen("sudo ip netns exec ns-%d ip link set dev veth%d up" % (container_pids[index+1], veth_index + 1), "r")

    setup_container_ovs(middle_container_cmds, name, veth_index - 1)

def run(num_containers, entry, exit):
    # create directory /var/run/netns if it doens't exist.
    # this is needed to peform the symlinking trick below
    # and get access to the network namespaces of the docker
    # containers 
    popen("sudo mkdir -p /var/run/netns", "r")

    container_names = []

    for i in range(num_containers):
        name = "container%d" % i
        #base_mid   = 'docker run --privileged -d --entrypoint=./ovs_alt.sh --name=%s --hostname=%s -v /mnt/huge:/mnt/huge -e DPDK_OPTIONS="%s" %s'

        base_mid   = 'docker run --privileged -d --name=%s --hostname=%s %s'

        base_entry = 'docker run -d --privileged --entrypoint=./ovs_alt.sh --name=%s --hostname=%s -v /mnt/huge:/mnt/huge --device=/dev/uio0:/dev/uio0 --device=/dev/uio1:/dev/uio1 -e DPDK_OPTIONS="%s" -v sockets:/usr/local/var/run/openvswitch/sockets %s'

        base_exit  = 'docker run -d --privileged --entrypoint=./ovs_alt.sh  --name=%s --hostname=%s -v /mnt/huge:/mnt/huge --device=/dev/uio0:/dev/uio0 --device=/dev/uio1:/dev/uio1 -e DPDK_OPTIONS="%s" --volumes-from container0 %s'

        if i == 0:
            opts = '-l 0,1,2,3,4 --master-lcore=4 -n 4 -w %s --file-prefix=m0 --socket-mem=1024,0' % (str(entry[1]))
            cmd = base_entry % (
                    name,
                    name,
                    opts,
                    IMAGE_NAME
                )

        elif i == num_containers - 1:
            vdev_str = "--vdev=virtio_user0,path=/usr/local/var/run/openvswitch/sockets/vhost-user-1"
            opts = '-l 10,11,12,13,14 --master-lcore=14 -n 4 -w %s --file-prefix=m1 --socket-mem=1024,0 %s' % (str(exit[1]), "")

            cmd = base_exit % (
                    name,
                    name,
                    opts,
                    IMAGE_NAME
                )
        else:
            cmd = base_mid % (name, name, IMAGE_NAME_mid)

            #opts = '-c 0x1 -n 4 --file-prefix=m3 --socket-mem=1024,0'
            #cmd = base_mid % (name, name, opts, IMAGE_NAME)

        popen(cmd, "r")
        container_names.append(name)

    print("sleeping..")
    sleep(2)
    print("waking up..")

    print("container_names: %s\n" % container_names)

    # find container pids and store in a list
    container_pids = [int(popen("docker inspect --format '{{.State.Pid}}' %s" % c).read().strip()) for c in container_names]

    #container_pids = [123, 321, 455]
    print("pids: %s" % container_pids)

    #enable ip commands to manipulate container namespace by creating a symlink
    [popen("sudo ln -s /proc/%d/ns/net /var/run/netns/ns-%d" % (pid, pid)) for pid in container_pids]

    veth_index = 0

    for index, pid in enumerate(container_pids):

        if index == 0: # first (entry point) container
            setup_entry_container(container_names[index], veth_index, container_pids, index, entry)
            veth_index += 2
             
        elif index == len(container_pids)-1: # last container of the chain
            setup_exit_container(container_names[index], veth_index-1, container_pids, index, exit)
            veth_index += 2

        else: # one of the 'middle' containers of the chain
            setup_middle_container(container_names[index], veth_index, container_pids, index)
            veth_index += 2

def dump_n_containers():
    with open(CONTAINERS_FILE, "w") as f:
        f.write("%d\n" % settings['num_containers'])

def load_n_containers():
    with open(CONTAINERS_FILE, "r") as f:
        return int(f.read().strip())

def stop_and_remove_container(n):
    container_name = "container%d" % n
    print(popen("docker stop %s" % container_name, "r")).read()
    print(popen("docker rm %s" % container_name, "r")).read()


def reset():
    """
        * stop docker containers
        * unbind interfaces from dpdk driver
        * rebind interfaces to kernel driver
        * remove huge page mappings
        * remove symlinks from /var/run/netns/
    """

    print("stopping containers..")
    for i in range(load_n_containers()):
        stop_and_remove_container(i)

    with open(INTERFACE_FILE, "r") as f:
        lines = [l.strip() for l in f.readlines()]
        for line in lines:
            iface = eval(line)

            print("unbinding from PMD: %s\n" % str(iface[0]))
            popen('./run.sh "--unbind %s"' % iface[1], "r")

            print("rebinding to kernel driver: %s\n" % iface[0])
            popen('./run.sh "--bind=%s %s"' % (iface[2], iface[1]), "r")

            print("rebinding interface %s to ip addr %s\n" % (iface[0], iface[4]))
            popen("ifconfig %s %s" % (iface[0], iface[4]), "r")


    print("clearing hugepage mappings.,\n")
    clear_huge_pages()

    print("removing symlinks from /var/run/netns/..\n")
    popen("sudo rm /var/run/netns/ns-*", "r")

    print("all done. exiting\n")
    exit(0)

def interfaces(entry, exit):
    entry_addr = interface_to_pci_addr(entry)
    exit_addr  = interface_to_pci_addr(exit)

    entry_driver = interface_driver(entry)
    exit_driver  = interface_driver(exit)

    entry_mac    = interface_mac(entry)
    exit_mac     = interface_mac(exit)

    entry_ip     = interface_ip(entry)
    exit_ip      = interface_ip(exit)

    return (entry, entry_addr, entry_driver, entry_mac, entry_ip),(exit, exit_addr, exit_driver, exit_mac, exit_ip)

def interface_to_pci_addr(iface):
    addr = popen('%s --status | grep unused=igb_uio | grep %s | cut -f 1 -d " "' % 
            (DEVBIND_SCRIPT, iface), "r").read()

    if len(addr) > 1:
        return addr.strip()

    raise RuntimeError("Unable to find pci addr for device %s" % iface)

def bind_iface(iface):
    popen("ip link set dev %s down" % iface[0], "r")
    popen("%s --bind=igb_uio %s" % (DEVBIND_SCRIPT, iface[0]), "r")

def usage():
    print("""
    usage: %s <entry interface> <exit interface>
    """ % sys.argv[0])
    sys.exit()

def interface_driver(iface):
    output = popen("./run.sh -s | grep %s" % iface, "r").read()
    if output:
        start = output.find("drv=") + len("drv=")
        end   = output[start:].find(" ") + start
        return output[start:end]

    raise RuntimeError("Unable to find kernerl driver of device %s" % iface)

def interface_mac(iface):
    output = popen("ip link show %s" % iface, "r").read()
    if not output:
        raise RuntimeError("Unable to find mac addr of device %s" % iface)

    start  = output.find("link/ether") + len("link/ether") + 1
    end    = output[start+1:].find(" ") + start + 1

    return output[start:end].strip()

def interface_ip(iface):
    output = popen("ip addr show %s" % iface, "r").read()
    if not output:
        raise RuntimeError("Unable to find ip addr of device %s" % iface)

    start = output.find("inet ") + len("inet ")
    end   = output[start:].find("/") + start
    return output[start:end].strip()

def dump_interfaces(entry, exit):
    print("dumping interfaces..")
    print(str(entry))
    print(str(exit))

    with open(INTERFACE_FILE, "w") as f:
        f.write("%s\n" % str(entry))
        f.write("%s\n" % str(exit))


def insert_kmods():
    popen("./insert_kernel_modules.sh", "r")

def mount_hugepages():
    popen("./%s" % HUGEPAGE_SCRIPT, "r")

def clear_huge_pages():
    popen("./clear_huge_pages.sh", "r")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        usage()
        
    insert_kmods()

    parse_args(sys.argv[1:])

    try:
        if settings['entry_iface'] and settings['exit_iface']:
            entry, exit = interfaces(settings['entry_iface'], settings['exit_iface'])
            dump_interfaces(entry, exit)
            print("entry %s, exit: %s\n" % (entry, exit))
    except RuntimeError as e:
        print("something went wrong: %s\n\n" % e)
        exit(1)

    bind_iface(entry)
    bind_iface(exit)
    mount_hugepages()
    #start_container(CONTAINER_NAME, entry, exit)
    if settings['num_containers']:
        dump_n_containers()
        run(settings['num_containers'], entry, exit)

    if settings['phoronix']:
        run_phoronix()
