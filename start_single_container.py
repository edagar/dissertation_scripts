#! /usr/bin/python2

from os import popen as _popen
import sys
from time import sleep
import argparse
from multiprocessing import Process


DPDK_SCRIPT_DIR = "/local/gitstuff/MoonGen/libmoon/deps/dpdk/tools"
DPDK_KMOD_DIR   = "/local/gitstuff/MoonGen/libmoon/deps/dpdk/x86_64-native-linuxapp-gcc/kmod"
DEVBIND_SCRIPT  = "%s/dpdk-devbind.py" % DPDK_SCRIPT_DIR
CONTAINER_NAME  = "ovs"
IMAGE_NAME      = "edagar/ovs-dpdk2"
HUGEPAGE_SCRIPT = "setup-hugetlbfs.sh"
INTERFACE_FILE  = "bound_interfaces"

DEFAULT_DPDK_MEM         = "1024,0"
DEFAwLT_DPDK_CORES       = "0-8"
DEFAULT_DPDK_PMD_MASK    = "0x5"
DEFAULT_DPDK_COREMASK    = "0xf"
DEFAULT_DPDK_NRXQ        = "4"
DEFAULT_DPDK_NTXQ        = "4"
DEFAULT_DPDK_MASTERCORE  = "8"
EXTRA_DOCKER_OPTIONS     = ""

def popen(a, b="r"):
    print("%s\n" % a)
    return _popen(a, b)

def start_container(name, entry, exit):
    dpdk_mem = DEFAULT_DPDK_MEM
    dpdk_cores = DEFAULT_DPDK_CORES
    dpdk_pmd_mask = DEFAULT_DPDK_PMD_MASK
    dpdk_coremask = DEFAULT_DPDK_COREMASK
    dpdk_mastercore = DEFAULT_DPDK_MASTERCORE
    dpdk_nrxq = DEFAULT_DPDK_NRXQ

    base = 'docker run -d --privileged %s --entrypoint=./run_ovs.sh --name=%s --hostname=%s -v /mnt/huge:/mnt/huge --device=/dev/uio0:/dev/uio0 --device=/dev/uio1:/dev/uio1 -e DPDK_OPTIONS="%s" %s'

    opts = '-l %s --master-lcore=%s -n 4 --file-prefix=ovscontainer --socket-mem=%s' % (dpdk_cores, dpdk_mastercore,  dpdk_mem)

    cmd = base % (EXTRA_DOCKER_OPTIONS, name, name, opts, IMAGE_NAME)
    popen(cmd, "r") 

    popen("sudo docker exec %s ovs-vsctl set Open_vSwitch . other_config:pmd-cpu-mask=%s" % (name, dpdk_pmd_mask))
    
    popen("docker exec %s ovs-vsctl del-br br0" % name, "r")
    popen("docker exec %s ovs-vsctl add-br br0 -- set bridge br0 datapath_type=netdev" % name, "r")

    popen("docker exec %s ovs-vsctl add-port br0 dpdk0 -- set Interface dpdk0 type=dpdk options:dpdk-devargs=%s" % (name, str(entry[1])), "r")
    popen("docker exec %s ovs-vsctl add-port br0 dpdk1 -- set Interface dpdk1 type=dpdk options:dpdk-devargs=%s" % (name, str(exit[1])), "r")

    popen("docker exec %s ovs-vsctl set Interface dpdk0 options:n_rxq=%s" % (name, dpdk_nrxq))
    popen("docker exec %s ovs-vsctl set Interface dpdk0 options:n_rxq_desc=128" % name)
    popen('docker exec %s ovs-vsctl set interface dpdk0 other_config:pmd-rxq-affinity="0:0"' % name)

    popen('docker exec %s ovs-ofctl add-flow br0 "in_port=1, actions=output:2"' % (name), "r")

    popen('docker exec %s ovs-ofctl add-flow br0 "in_port=2, actions=output:1"' % (name), "r")

def interface_to_pci_addr(iface):
    addr = popen('%s --status | grep unused=igb_uio | grep %s | cut -f 1 -d " "' % 
            (DEVBIND_SCRIPT, iface), "r").read()

    if len(addr) > 1:
        return addr.strip()

    raise RuntimeError("Unable to find pci addr for device %s" % iface)

def bind_iface(iface):
    popen("ip link set dev %s down" % iface[0], "r")
    popen("%s --bind=vfio-pci %s" % (DEVBIND_SCRIPT, iface[0]), "r")

def usage():
    print("""
    usage: %s -i <entry interface> -o <exit interface>..
    """ % sys.argv[0])
    sys.exit(1)

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

def dump_interfaces(entry, exit, dumpfile):
    print("dumping interfaces..")
    print(str(entry))
    print(str(exit))

    with open(dumpfile, "w") as f:
        f.write("%s\n" % str(entry))
        f.write("%s\n" % str(exit))

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

def reset():
    """
        * stop docker container
        * unbind interfaces from dpdk driver
        * rebind interfaces to kernel driver
        * rebind interfaces to previous ip addrs
        * remove huge page mappings
    """

    print("stopping container..")
    popen("docker stop %s" % (CONTAINER_NAME), "r")
    popen("docker rm %s" % (CONTAINER_NAME), "r")

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

    print("clearing hugepages..\n")
    clear_huge_pages()

def insert_kmods():
    popen("./insert_kernel_modules.sh", "r")

def mount_hugepages():
    popen("./%s" % HUGEPAGE_SCRIPT, "r")

def clear_huge_pages():
    popen("./clear_huge_pages.sh", "r")

def setup_env(i0, i1, dumpfile, run_container=True):
    """
        - insert kernel modules
        - bind interfaces
        - mount hugepages
        - start container
        - setup ovs-dpdk inside container
    """

    insert_kmods()

    try:
        entry, exit = interfaces(i0, i1)
        dump_interfaces(entry, exit, dumpfile)
        print("entry %s, exit: %s\n" % (entry, exit))
    except RuntimeError as e:
        print("something went wrong: %s\n\n" % e)
        exit(1)

    bind_iface(entry)
    bind_iface(exit)
    mount_hugepages()

    if run_container:
        start_container(CONTAINER_NAME, entry, exit)   

def _usage():
    print("atleast one of the following cmdline options is needed:\n\t*--entry and --exit\n\t*--reset\n\t*--phoronix\n\n")

def find_phoronix_number():
    lines = popen('docker ps -a | egrep -o  "phoronix([0-100])?$"').readlines()
    if not lines:
        return 0

    numbers = [int(line.strip()[-1:]) for line in lines if line.strip()[-1].isdigit()]
    if not numbers:
        return 0

    return max(numbers)+1

def run_phoronix_benchmark():
    name = "phoronix%d" % (find_phoronix_number())

    print("starting phoronix benchmark container (name: %s)\n" % (name))
    popen('docker run -d --entrypoint=./run.sh --name=%s -e COMMAND="benchmark pts/apache" edagar/phoronix' % (name), "r")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()

    parser.add_argument('--reset', action='store_const', const=True, default=None)
    parser.add_argument('--cores', '-c')
    parser.add_argument('--mem', '-m')
    parser.add_argument('--pmd_mask', '-p')
    parser.add_argument('--n_rxq')
    parser.add_argument('--n_txq')
    parser.add_argument('--master_core')
    parser.add_argument('--cpus')
    parser.add_argument('--phoronix', action='store_const', const=True, default=None)
    parser.add_argument('--entry', '-i')
    parser.add_argument('--exit', '-o')

    args = parser.parse_args()

    if (args.entry or args.exit):
        if not (args.entry and args.exit):
            print("Need to specify entry and exit interfaces (got only one)\n\n")
            parser.print_help()
            parser.exit()

    if not (args.reset or (args.entry and args.exit) or args.phoronix):
        _usage()
        parser.print_usage()
        parser.exit()

    if args.mem:
        DEFAULT_DPDK_MEM = args.mem

    if args.cores:
        DEFAULT_DPDK_CORES = args.cores

    if args.pmd_mask:
        DEFAULT_DPDK_PMD_MASK = args.pmd_mask

    if args.n_rxq:
        DEFAULT_DPDK_NRXQ = args.n_rxq

    if args.n_txq:
        DEFAULT_DPDK_NTXQ = args.n_txq

    if args.master_core:
        DEFAULT_DPDK_MASTERCORE = args.master_core

    if args.cpus:
        EXTRA_DOCKER_OPTIONS += "--cpus=%s" % args.cpus

    if args.reset:
        reset()

    if args.phoronix:
        phoronix_process = Process(target=run_phoronix_benchmark)
        phoronix_process.start()

    if args.entry and args.exit:
        print("setting up benchmark environment (entry: %s, exit: %s)\n" % 
                (args.entry, args.exit)
             )
        setup_env(args.entry, args.exit, INTERFACE_FILE)

    if args.phoronix:
        print("joining phoronix process..\n")
        phoronix_process.join()

