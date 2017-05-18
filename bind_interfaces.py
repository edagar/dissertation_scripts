#! /usr/bin/python2

import sys
from os import popen as _popen
from time import sleep

HUGEPAGE_SCRIPT = "setup-hugetlbfs.sh"

def popen(a, b="r"):
    sleep(1)
    print("%s\n" % a)
    return _popen(a, b)

def insert_kmods():
    popen("./insert_kernel_modules.sh", "r")

def mount_hugepages():
    popen("./%s" % HUGEPAGE_SCRIPT, "r")

def bind_iface(iface):
    print("binding interface %s..\n" % iface)

    popen("ip link set dev %s down" % iface, "r")
    #popen('./run.sh "--bind=igb_uio %s"' % iface, "r")
    popen('./run.sh "--bind=vfio_pci %s"' % iface, "r")

if __name__ == "__main__":
    if len(sys.argv) == 1:
        sys.exit(1)

    args = sys.argv[1:]
    
    if "--insert-kernel-modules" in args:
        insert_kmods()
        _ = args.pop(args.index("--insert-kernel-modules"))

    if "--mount-hugepages" in args:
        mount_hugepages()
        _ = args.pop(args.index("--mount-hugepages"))

    for iface in args:
        bind_iface(iface)
